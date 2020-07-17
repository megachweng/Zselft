import os
import pathlib
import platform
import shutil
import sys
import logging
from threading import Thread

import requests
from PyQt5.QtGui import QPixmap, QIcon
from python_hosts import Hosts, HostsEntry
from ui.qt_log_handler import QLogHandler
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QListWidgetItem
from PyQt5.QtCore import pyqtSlot, QCoreApplication, QSize, Qt
from ui.mainForm import Ui_Window
from ui.account_dialog import AddAccountDialog
from utls import is_admin, add_cert, zwift_user_profile_interpreter, FileDialog

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
STORAGE_PATH = os.path.join(cwd, 'storage')


class Window(QWidget, Ui_Window):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.connect_sig()
        self.fake_server_thread = None
        self.zwift_folder = None
        self.show()
        self.stopServiceBtn.setEnabled(False)
        self.start_fake_server()
        self.list_profiles()
        self.load_config()

    def load_config(self):
        config_file = os.path.join(STORAGE_PATH,'config.ini')

        self.zwift_folder = FileDialog()

    def connect_sig(self):
        q_log_handler.newRecord.connect(self.logMonitor.appendPlainText)

    def list_profiles(self):
        self.AccountListWidget.clear()
        self.AccountListWidget.setIconSize(QSize(50, 50))
        for _, dirs, _ in os.walk(STORAGE_PATH):
            for profile_id in dirs:
                file_path = os.path.join(STORAGE_PATH, profile_id, 'profile.bin')
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as fd:
                        user_info = zwift_user_profile_interpreter(fd.read())

                    with open(os.path.join(STORAGE_PATH, profile_id, 'avatar'), 'rb') as fp:
                        pixmap = QPixmap()
                        pixmap.loadFromData(fp.read())
                    icon = QIcon(pixmap)
                    item = QListWidgetItem(icon, f'{user_info["first_name"]} {user_info["last_name"]}')
                    item.setData(Qt.UserRole, str(user_info['uid']))
                    self.AccountListWidget.addItem(item)

    @pyqtSlot(bool)
    def on_addAccountBtn_clicked(self):
        account_dialog = AddAccountDialog(parent=self)
        save_or_not = account_dialog.exec_()
        if save_or_not:
            try:
                account_dict = account_dialog.account_dict
                p = pathlib.Path(os.path.join(STORAGE_PATH, str(account_dict['uid'])))
                p.mkdir(parents=True, exist_ok=True)

                # save profile.bin
                with open((p / 'profile.bin'), 'wb') as f:
                    f.write(account_dict['profile.bin'])
                # save avatar
                with open((p / 'avatar'), 'wb') as fp:
                    fp.write(account_dict['avatar'])
                # save strava_token.txt
                with open((p / 'strava_token.txt'), 'w') as fp:
                    fp.write(account_dict['strava_token.txt'])

                # save garmin
                garmin_username = account_dialog.garminUsernameEdit.text()
                garmin_password = account_dialog.garminPasswordEdit.text()
                if all([garmin_username, garmin_password]):
                    with open((p / 'garmin_credentials.txt'), 'w') as fp:
                        fp.write(garmin_username + "\n" + garmin_password)
            except Exception as e:
                logger.exception(e)
        else:
            logger.info('取消保存')
        self.list_profiles()

    @pyqtSlot(bool)
    def on_deleteAccountBtn_clicked(self):
        item = self.AccountListWidget.currentIndex()
        logger.info(item.data(Qt.UserRole))
        shutil.rmtree(os.path.join(STORAGE_PATH, item.data(Qt.UserRole)))
        self.list_profiles()

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
        add_cert(zwift_path=self.zwift_folder)

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
