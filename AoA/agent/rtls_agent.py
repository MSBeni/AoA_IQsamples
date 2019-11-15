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
#     its contributors m♦ay be used to endorse or promote products derived
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

import argparse

import logging
import sys
import typing
import dataclasses
from dataclasses import dataclass
from time import strftime, gmtime

from rtls import RTLSManager
from rtls import RTLSNode, NodeMessage
import serial.tools.list_ports as list_ports

from PySide2.QtGui import QCloseEvent
from PySide2.QtCore import Signal, Slot, QEvent, \
    QObject
from PySide2.QtWidgets import QMainWindow, QApplication, QTreeWidgetItem
from rtls_agent_ui import Ui_MainWindow
from serial_selection import NodeSelectDialog

import json

def ws_status_update(signal, action):
    def update_ws_status(ws):
        signal.emit(action)
    return update_ws_status


@dataclass
class RtlsGuiMessage:
    time: str
    sender: str
    receiver: str
    subsys: str
    cmd: str
    data: typing.Any


def ws_message(signal):
    def inner(nodemsg):
        identifier = nodemsg.identifier
        msg = nodemsg.message.item
        subsys = msg.subsystem.name if hasattr(msg.subsystem, 'name') else msg.subsystem
        cmd = msg.command.name if hasattr(msg.command, 'name') else msg.command

        gui_msg = RtlsGuiMessage(strftime('%H:%M:%S', gmtime()), 'socket', identifier, subsys, cmd, msg.dict)
        signal.emit(gui_msg)
    return inner


class EvReceiver(QObject):
    def __init__(self, parent, event_callback):
        QObject.__init__(self, parent)
        self.callback = event_callback

    def event(self, event: QEvent):
        if event.type() == QEvent.User:
            self.callback(event.my_data)
        else:
            return super().event(event)
        return True


class CustomEvent(QEvent):
    def __init__(self, _type, my_data):
        super().__init__(_type)
        self.my_data = my_data


class RTLSAgent(QMainWindow):
    sig_socket_status = Signal(str)
    sig_socket_msg = Signal(RtlsGuiMessage)

    def __init__(self, ws_port):
        super().__init__()
        self.ws_port = ws_port

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.lblWebsocket.setText(f"WebSocket Server, ws://localhost:{ws_port}")
        self.ui.lblWebsocketStatus.setText(f"Waiting for connection")

        self.sig_socket_status.connect(self.ui.lblWebsocketStatus.setText)
        self.sig_socket_msg.connect(self.add_log_message)

        self.nodes = []
        self.manager = None

        self.ev_receiver = EvReceiver(self, self.receive_node_message)

    @Slot(RtlsGuiMessage)
    def add_log_message(self, msg: RtlsGuiMessage):
        self.ui.viewLog.insertTopLevelItem(0, QTreeWidgetItem(None, dataclasses.astuple(msg)))

    def add_nodes(self, nodes):
        self.nodes += nodes

    def start_manager(self, nodes=None):
        if nodes:
            self.add_nodes(nodes)

        # self.managerSub = Subscriber(queue=queue.PriorityQueue(), interest=None, transient=False, eventloop=None)

        try:
            self.manager = RTLSManager(self.nodes, self.ws_port)
            self.manager.auto_params = True

            # self.manager.add_subscriber(self.managerSub)
            self.manager.on_ws_connect = ws_status_update(self.sig_socket_status, 'connected')
            self.manager.on_ws_disconnect = ws_status_update(self.sig_socket_status, 'disconnected')
            self.manager.on_ws_message = ws_message(self.sig_socket_msg)
            self.manager.on_node_message = lambda x: QApplication.postEvent(self.ev_receiver, CustomEvent(QEvent.User, x), 0)
            self.manager.start()

            for node in self.manager.nodes:
                logging.info(node.identifier)

        except Exception as e:
            self.manager.stop()
            raise e

    @Slot(NodeMessage)
    def receive_node_message(self, node_msg):
        from_node = node_msg.identifier
        pri = node_msg.message.priority
        msg = node_msg.message.item
        logging.info(node_msg.as_json())

        gui_msg = RtlsGuiMessage(strftime('%H:%M:%S', gmtime()), from_node, 'socket', msg.subsystem, msg.command,
                                 json.dumps(json.loads(msg.as_json())['payload']))
        self.sig_socket_msg.emit(gui_msg)

    def closeEvent(self, event: QCloseEvent):
        self.manager.stop()
        event.accept()


def main():
    #
    # Command line parsing
    #
    parser = argparse.ArgumentParser(description="Start an RTLS/uNPI web-socket server")
    parser.add_argument('-p', '--port', dest="port", type=int, default=8766, metavar="PORT",
                        help="Port for websocket ws://localhost:PORT")
    parser.add_argument('-d', '--device', dest="devices", type=str, nargs=2, action="append", metavar=('PORT', 'NAME'),
                        help="Add device, eg. -d COM48 TOFMaster")
    parser.add_argument('--debuglog', action='store_true', help="Saves logging info to 'socketserver_log.txt'")
    parser.add_argument('-l', '--list-ports', action='store_true', help="Print list of serial ports")

    #
    #  Pycharm workaround
    #
    _argv = sys.argv
    if '--file' in _argv:
        _argv = _argv[_argv.index('--file') + 1:]

    # if len(_argv[1:]) == 0:
    #     parser.print_help()
    #     parser.exit()

    args = parser.parse_args(_argv[1:])

    if args.list_ports:
        for x in list_ports.comports():
            print(f"  {x.device} - {x.description}")
        parser.exit()

    if args.debuglog:
        logging.basicConfig(
            # stream=sys.stdout,
            filename="rtls_agent_log.txt",
            filemode="w",
            level=logging.DEBUG,
            format='[%(asctime)s] %(filename)-18sln %(lineno)3d %(threadName)-10s %(levelname)8s - %(message)s')

    if args.devices:
        my_nodes = [RTLSNode(port, 115200, name) for port, name in args.devices]
    else:
        my_nodes = []

    app = QApplication([])
    agent = RTLSAgent(args.port)
    dialog = NodeSelectDialog()

    if len(my_nodes) == 0:
        def choose_done():
            agent.start_manager(dialog.get_selected())
            dialog.close()
            agent.show()

        dialog.accepted.connect(choose_done)
        dialog.rejected.connect(sys.exit)
        dialog.show()
    else:
        agent.start_manager(my_nodes)
        agent.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

