import os
import platform
import sys
import logging
from threading import Thread
from python_hosts import Hosts, HostsEntry
from ui.qt_log_handler import QLogHandler
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from ui.mainForm import Ui_Window
from ui.account_dialog import AddAccountDialog
from utls import is_admin, add_cert

import standalone

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
q_log_handler = QLogHandler()
logger.addHandler(q_log_handler)

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
cwd = os.getcwd()


class Window(QWidget, Ui_Window):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.connect_sig()
        self.fake_server_thread = None
        self.show()
        self.stopServiceBtn.setEnabled(False)
        self.start_fake_server()

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

        if platform.system() != 'Windows':
            logger.error('只支持Windows系统')
            return

        if not is_admin():
            box = QMessageBox()
            box.setText("请用管理员身份运行！")
            box.setStandardButtons(QMessageBox.Yes)
            box.exec()
            QCoreApplication.instance().quit()
            return

        self.stopServiceBtn.setEnabled(True)
        self.startServiceBtn.setEnabled(False)
        self.edit_host(enable=True)
        add_cert()

    @pyqtSlot(bool)
    def on_stopServiceBtn_clicked(self):
        self.stopServiceBtn.setEnabled(False)
        self.startServiceBtn.setEnabled(True)
        self.stop_service()

    def start_fake_server(self):
        t = Thread(target=standalone.start)
        t.daemon = True
        t.start()
        pass

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
        if self.fake_server_thread is not None:
            self.fake_server_thread.terminate()
            logger.info('服务终止')
            self.fake_server_thread = None
        self.edit_host(enable=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())
