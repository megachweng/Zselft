# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Window(object):
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.resize(668, 413)
        self.gridLayout_2 = QtWidgets.QGridLayout(Window)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.logMonitor = QtWidgets.QPlainTextEdit(Window)
        self.logMonitor.setAcceptDrops(False)
        self.logMonitor.setAutoFillBackground(False)
        self.logMonitor.setReadOnly(True)
        self.logMonitor.setObjectName("logMonitor")
        self.gridLayout_2.addWidget(self.logMonitor, 0, 2, 2, 1)
        self.startServiceBtn = QtWidgets.QPushButton(Window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startServiceBtn.sizePolicy().hasHeightForWidth())
        self.startServiceBtn.setSizePolicy(sizePolicy)
        self.startServiceBtn.setMinimumSize(QtCore.QSize(0, 100))
        self.startServiceBtn.setObjectName("startServiceBtn")
        self.gridLayout_2.addWidget(self.startServiceBtn, 1, 0, 1, 1)
        self.stopServiceBtn = QtWidgets.QPushButton(Window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopServiceBtn.sizePolicy().hasHeightForWidth())
        self.stopServiceBtn.setSizePolicy(sizePolicy)
        self.stopServiceBtn.setMinimumSize(QtCore.QSize(0, 100))
        self.stopServiceBtn.setObjectName("stopServiceBtn")
        self.gridLayout_2.addWidget(self.stopServiceBtn, 1, 1, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.deleteAccountBtn = QtWidgets.QPushButton(Window)
        self.deleteAccountBtn.setObjectName("deleteAccountBtn")
        self.gridLayout.addWidget(self.deleteAccountBtn, 1, 0, 1, 1)
        self.addAccountBtn = QtWidgets.QPushButton(Window)
        self.addAccountBtn.setObjectName("addAccountBtn")
        self.gridLayout.addWidget(self.addAccountBtn, 1, 1, 1, 1)
        self.AccountListWidget = QtWidgets.QListWidget(Window)
        self.AccountListWidget.setObjectName("AccountListWidget")
        self.gridLayout.addWidget(self.AccountListWidget, 0, 0, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 2)

        self.retranslateUi(Window)
        QtCore.QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        _translate = QtCore.QCoreApplication.translate
        Window.setWindowTitle(_translate("Window", "Window"))
        self.startServiceBtn.setText(_translate("Window", "自闭"))
        self.stopServiceBtn.setText(_translate("Window", "复原"))
        self.deleteAccountBtn.setText(_translate("Window", "-"))
        self.addAccountBtn.setText(_translate("Window", "+"))
        __sortingEnabled = self.AccountListWidget.isSortingEnabled()
        self.AccountListWidget.setSortingEnabled(False)
        self.AccountListWidget.setSortingEnabled(__sortingEnabled)
