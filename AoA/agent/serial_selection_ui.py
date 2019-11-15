# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'agent/serial_selection.ui',
# licensing of 'agent/serial_selection.ui' applies.
#
# Created: Tue Feb 19 15:49:31 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(657, 336)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/main/ti.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chkFilter = QtWidgets.QCheckBox(Dialog)
        self.chkFilter.setObjectName("chkFilter")
        self.horizontalLayout.addWidget(self.chkFilter)
        self.btnDetect = QtWidgets.QPushButton(Dialog)
        self.btnDetect.setObjectName("btnDetect")
        self.horizontalLayout.addWidget(self.btnDetect)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.viewDevices = QtWidgets.QTreeView(Dialog)
        self.viewDevices.setIndentation(0)
        self.viewDevices.setUniformRowHeights(True)
        self.viewDevices.setItemsExpandable(False)
        self.viewDevices.setObjectName("viewDevices")
        self.verticalLayout.addWidget(self.viewDevices)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Connect Serial RTLS Nodes", None, -1))
        self.chkFilter.setWhatsThis(QtWidgets.QApplication.translate("Dialog", "Whether to filter the serial ports based on XDS110 being in the description", None, -1))
        self.chkFilter.setText(QtWidgets.QApplication.translate("Dialog", "Filter Launchpads", None, -1))
        self.btnDetect.setWhatsThis(QtWidgets.QApplication.translate("Dialog", "Connect to each serial port and send IDENTIFY command", None, -1))
        self.btnDetect.setText(QtWidgets.QApplication.translate("Dialog", "Auto-detect", None, -1))
        self.viewDevices.setWhatsThis(QtWidgets.QApplication.translate("Dialog", "List of serial ports", None, -1))

import rtls_agent_rc
