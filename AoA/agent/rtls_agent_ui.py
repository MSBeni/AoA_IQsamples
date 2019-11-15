# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'agent/rtls_agent.ui',
# licensing of 'agent/rtls_agent.ui' applies.
#
# Created: Tue Feb 19 15:49:29 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(875, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/main/ti.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblWebsocket = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblWebsocket.sizePolicy().hasHeightForWidth())
        self.lblWebsocket.setSizePolicy(sizePolicy)
        self.lblWebsocket.setObjectName("lblWebsocket")
        self.horizontalLayout.addWidget(self.lblWebsocket)
        self.lblWebsocketStatus = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblWebsocketStatus.sizePolicy().hasHeightForWidth())
        self.lblWebsocketStatus.setSizePolicy(sizePolicy)
        self.lblWebsocketStatus.setObjectName("lblWebsocketStatus")
        self.horizontalLayout.addWidget(self.lblWebsocketStatus)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.viewLog = QtWidgets.QTreeWidget(self.centralwidget)
        self.viewLog.setIndentation(0)
        self.viewLog.setUniformRowHeights(True)
        self.viewLog.setItemsExpandable(False)
        self.viewLog.setExpandsOnDoubleClick(True)
        self.viewLog.setColumnCount(6)
        self.viewLog.setObjectName("viewLog")
        self.verticalLayout.addWidget(self.viewLog)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 875, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL("triggered()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "RTLS Agent", None, -1))
        self.lblWebsocket.setText(QtWidgets.QApplication.translate("MainWindow", "Webscoket address", None, -1))
        self.lblWebsocketStatus.setText(QtWidgets.QApplication.translate("MainWindow", "Websocket Status", None, -1))
        self.viewLog.headerItem().setText(0, QtWidgets.QApplication.translate("MainWindow", "Time", None, -1))
        self.viewLog.headerItem().setText(1, QtWidgets.QApplication.translate("MainWindow", "Sender", None, -1))
        self.viewLog.headerItem().setText(2, QtWidgets.QApplication.translate("MainWindow", "Receiver", None, -1))
        self.viewLog.headerItem().setText(3, QtWidgets.QApplication.translate("MainWindow", "SubSystem", None, -1))
        self.viewLog.headerItem().setText(4, QtWidgets.QApplication.translate("MainWindow", "Command", None, -1))
        self.viewLog.headerItem().setText(5, QtWidgets.QApplication.translate("MainWindow", "Data", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.actionExit.setText(QtWidgets.QApplication.translate("MainWindow", "Exit", None, -1))
        self.actionExit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Alt+X", None, -1))

import rtls_agent_rc
