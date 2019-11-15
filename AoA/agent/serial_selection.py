#
#  Copyright (c) 2018-2019, Texas Instruments Incorporated
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  *  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  *  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  *  Neither the name of Texas Instruments Incorporated nor the names of
#     its contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import time
from dataclasses import dataclass

import serial.tools.list_ports as list_ports
from rtls import RTLSNode

from PySide2.QtWidgets import QApplication, QDialog
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, QRunnable, Slot, QObject, QThreadPool, \
    QSortFilterProxyModel, QRegExp

from serial_selection_ui import Ui_Dialog


@dataclass
class PortStatus:
    device: str
    description: str
    checked: bool
    rtls_node: RTLSNode or None
    connecting: bool = False
    no_rsp = False


class PortTableModel(QAbstractTableModel):
    def __init__(self, filter_launchpads, *args, **kwargs):
        QAbstractTableModel.__init__(self, *args, **kwargs)
        self.filter_launchpads = False

        self.current_ports, self.port_status = self._scan_ports(self.filter_launchpads, None)

        self.ports = sorted([v for k, v in self.port_status.items() if k in map(lambda x: x.device, self.current_ports)],
                            key=lambda x: x.device)

    def columnCount(self, parent=QModelIndex()):
        return 5

    def rowCount(self, parent=QModelIndex()):
        return len(self.current_ports)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount():
            if role == Qt.DisplayRole:
                port = self.ports[index.row()]
                col = index.column()
                if col == 0: return '✓' if port.checked else ''
                if col == 1: return port.device
                if col == 2: return 'Connecting' if port.connecting else 'No response' if port.no_rsp else 'n/a' if not port.rtls_node else port.rtls_node.identifier if port.rtls_node.identifier else 'n/a'
                if col == 3: return 'n/a' if not (port.rtls_node and port.rtls_node.capabilities) else ', '.join(
                             [str(c) for c, e in port.rtls_node.capabilities.items() if e])
                if col == 4: return port.description

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        titles = ['', 'Port', 'Identifier', 'Capabilities', 'Description']
        if role == Qt.DisplayRole:
            return titles[section]

    @staticmethod
    def _scan_ports(do_filter=True, current_status=None):
        def get_ports():
            if not do_filter:
                return list_ports.comports()
            return list_ports.grep('.*XDS110.*')

        current_ports = sorted(list(get_ports()), key=lambda x: x.device)
        if not current_status:
            port_status = {port.device: PortStatus(port.device, port.description, False, None) for port in current_ports}
        else:
            port_status = current_status
            for p in current_ports:
                if not p.device in port_status:
                    port_status[p.device] = PortStatus(p.device, p.description, False, None)

        return current_ports, port_status

    def refresh_ports(self, indices):
        if not len(indices):
            self.layoutChanged.emit()
        else:
            top_left = self.createIndex(min(indices), 0, 0)
            bottom_right = self.createIndex(max(indices), 3, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])

    def set_filter(self, state):
        self.filter_launchpads = state
        self.current_ports, self.port_status = self._scan_ports(self.filter_launchpads, self.port_status)
        self.ports = sorted([v for k, v in self.port_status.items() if k in map(lambda x: x.device, self.current_ports)],
                            key=lambda x: x.device)
        self.refresh_ports(range(self.rowCount()))


class NodeSelectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.filter_launchpads = True
        self.port_model = PortTableModel(self.filter_launchpads)
        self.threadpool = QThreadPool()

        self.widgets = {}
        self.central_widget = None

        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.port_model)
        self.proxyModel.setFilterRegExp(QRegExp(".*XDS110.*") if self.filter_launchpads else None)
        self.proxyModel.setFilterKeyColumn(4)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.chkFilter.setCheckState(Qt.Checked if self.filter_launchpads else Qt.Unchecked)
        self.ui.chkFilter.stateChanged.connect(self._filter_changed)
        self.ui.btnDetect.clicked.connect(self._auto_detect)
        self.ui.viewDevices.setModel(self.proxyModel)
        self.ui.viewDevices.doubleClicked.connect(self._connect_one)

        self.ui.viewDevices.setColumnWidth(0, 10)
        self.ui.viewDevices.setColumnWidth(1, 200)
        self.ui.viewDevices.setColumnWidth(2, 140)
        self.ui.viewDevices.setColumnWidth(3, 150)

    def _auto_detect(self):
        real_rows = [self.proxyModel.mapToSource(self.proxyModel.index(x, 0)).row() for x in range(self.proxyModel.rowCount())]
        self.threadpool.start(Worker(lambda: self._connect_rtls_nodes(real_rows)))

    def _connect_one(self, index: QModelIndex):
        row = self.proxyModel.mapToSource(index).row()
        self.threadpool.start(Worker(lambda: self._connect_rtls_nodes([row])))

    def _filter_changed(self, state):
        do_filter = True if state == Qt.Checked else False
        self.proxyModel.setFilterRegExp(QRegExp(".*XDS110.*") if do_filter else None)
        # self.port_model.set_filter(do_filter)

    def _connect_rtls_nodes(self, indices):
        statuses = [self.port_model.ports[i] for i in indices if len(indices) == 1 or self.port_model.ports[i].rtls_node is None]

        for status in statuses:
            if not status.rtls_node:
                status.connecting = True

        self.port_model.refresh_ports(indices)

        for status in statuses:
            node = status.rtls_node
            status.checked = False
            if node:
                node.stop()
                status.rtls_node = None
                status.checked = False
            else:
                node = status.rtls_node = RTLSNode(status.device, 115200, status.device)
                node.start()

        target_time = time.time() + 0.5
        waiters = [s for s in statuses if s.rtls_node]
        while target_time > time.time() and len(waiters):
            should_update = False
            for s in waiters:
                if s.rtls_node.identifyEvent.isSet():
                    should_update = True
                    s.connecting = False
                    s.checked = True
                    waiters.remove(s)

            if should_update:
                self.port_model.refresh_ports(indices)

        for status in statuses:
            status.connecting = False
            node = status.rtls_node
            if node:
                if node.exception:
                    print(node.exception)
                    # sg.Popup(str(node.exception), title="Exception")
                if node.identifier is None:
                    node.stop()
                    status.rtls_node = None
                    status.no_rsp = True

            self.port_model.refresh_ports(indices)

    def get_selected(self):
        return [x.rtls_node for x in self.port_model.port_status.values() if x.checked]


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


if __name__ == '__main__':
    app = QApplication([])

    selector = NodeSelectDialog()
    selector.show()
    ret = app.exec_()

    print(f"Return code {ret}")
    connected_nodes = selector.get_selected()
    print(connected_nodes)

    for n in connected_nodes:
        n.stop()
        n.wait_stopped()
