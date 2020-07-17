import os
import platform
import subprocess
import sys
import logging
from threading import Thread
from python_hosts import Hosts, HostsEntry
from qt_log_handler import QLogHandler
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from ui.mainForm import Ui_Window
from account_dialog import AddAccountDialog
from service import server
from utls import is_admin

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
q_log_handler = QLogHandler()
logger.addHandler(q_log_handler)


class Window(QWidget, Ui_Window):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.connect_sig()
        self.fake_server_thread = None
        self.show()
        self.stopServiceBtn.setEnabled(False)

    def connect_sig(self):
        q_log_handler.newRecord.connect(self.logMonitor.appendPlainText)
        self.addAccountBtn.clicked.connect(self.add_account)
        self.deleteAccountBtn.clicked.connect(self.del_account)

    @pyqtSlot()
    def add_account(self):
        account_dialog = AddAccountDialog(parent=self)
        save_or_not = account_dialog.exec_()
        if save_or_not:
            logger.info(account_dialog.zwiftUsernameEdit.text())
        else:
            logger.info('取消保存')

    @pyqtSlot()
    def del_account(self):
        logger.info('删除')

    @pyqtSlot(bool)
    def on_startServiceBtn_clicked(self):
        if not is_admin():
            box = QMessageBox()
            box.setText("请用管理员身份运行！")
            box.setStandardButtons(QMessageBox.Yes)
            box.exec()
            QCoreApplication.instance().quit()
            return

        if self.fake_server_thread is None:
            self.start_fake_server()

        self.stopServiceBtn.setEnabled(True)
        self.startServiceBtn.setEnabled(False)
        self.edit_host(enable=True)

    @pyqtSlot(bool)
    def on_stopServiceBtn_clicked(self):
        self.stopServiceBtn.setEnabled(False)
        self.startServiceBtn.setEnabled(True)
        self.stop_service()

    def start_fake_server(self):
        logger.info('Start Fake Server')
        if platform.system() == 'Windows':
            NO_WINDOW = 0x08000000
            pip = subprocess.Popen(
                [sys.executable, 'service/server.py'],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=NO_WINDOW)

        elif platform.system() == 'Darwin':
            pip = subprocess.Popen(
                [sys.executable, 'service/server.py'],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
        else:
            logger.error('System Not Supported')

    def edit_host(self, enable):
        hosts = Hosts()
        if enable:
            entry = HostsEntry(entry_type='ipv4', address='127.0.0.1',
                               names=['us-or-rly101.zwift.com', 'secure.zwift.com', 'cdn.zwift.com',
                                      'launcher.zwift.com'])
            hosts.add([entry])
        else:
            hosts.remove_all_matching(name='cdn.zwift.com')
        logger.info(hosts.write())

    def closeEvent(self, event):
        self.edit_host(enable=False)
        event.accept()

    def stop_service(self):
        logger.info('服务终止')
        self.edit_host(enable=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())
