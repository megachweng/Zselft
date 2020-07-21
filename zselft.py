import json
import os
import pathlib
import platform
import shutil
import sys
import logging
from logging.handlers import RotatingFileHandler
from xml.etree import ElementTree
from threading import Thread
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QListWidgetItem
from PyQt5.QtCore import pyqtSlot, QCoreApplication, QSize, Qt
from python_hosts import Hosts, HostsEntry
from ui.qt_log_handler import QLogHandler
from ui.mainForm import Ui_Window
from ui.account_dialog import AddAccountDialog
from ui.profile_editor import ProfileEditor
from utls import is_admin, add_cert, zwift_user_profile_interpreter, choose_zwift_path
from const import LATEST_TESTED_ZWIFT_VERSION, CONFIG_FILE, BUNDLE_DIR, STORAGE_DIR_PATH
import standalone

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(asctime)s] %(message)s', '%d/%m/%Y %H:%M:%S')

q_log_handler = QLogHandler()
q_log_handler.setLevel(logging.INFO)
file_handler = RotatingFileHandler('zselft.log', maxBytes=3 * 10 ** 6, backupCount=10)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(q_log_handler)
logger.addHandler(file_handler)


def fatal_error(exc_type, exc_value, exc_traceback):
    logger.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


# 未知异常日志
sys.excepthook = fatal_error


class Window(QWidget, Ui_Window):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.connect_sig()
        self.fake_server_thread = None
        self.zwift_path = pathlib.Path('~').expanduser()
        self.show()
        self.stopServiceBtn.setEnabled(False)
        self.start_fake_server()
        self.list_profiles()
        self.load_config()
        self.check_zwift_version()

    def load_config(self):
        if CONFIG_FILE.is_file():
            with open(CONFIG_FILE) as fd:
                config = json.load(fd)
                self.zwift_path = pathlib.Path(config['zwift_path'])

        self.zwift_path = choose_zwift_path(self.zwift_path)

        with open(CONFIG_FILE, 'w') as fd:
            json.dump({'zwift_path': str(self.zwift_path)}, fd)

    def check_zwift_version(self):
        zwift_version_xml = os.path.join(self.zwift_path, 'Zwift_ver_cur.xml')
        tree = ElementTree.parse(zwift_version_xml)
        root = tree.getroot()
        version = root.attrib.get('version')
        logger.info(f'ZWIFT版本:{version}')
        if version == LATEST_TESTED_ZWIFT_VERSION:
            return
        else:
            shutil.copyfile(zwift_version_xml, BUNDLE_DIR / 'cdn/gameassets/Zwift_Updates_Root/Zwift_ver_cur.xml')
            logger.info('Copy zwift version file')

    def connect_sig(self):
        q_log_handler.newRecord.connect(self.logMonitor.appendPlainText)
        self.AccountListWidget.itemDoubleClicked.connect(self.edit_profile)

    def edit_profile(self, item):
        zwift_uid = item.data(Qt.UserRole)
        profile_editor = ProfileEditor(zwift_uid=zwift_uid, parent=self)
        profile_editor.exec_()

    def list_profiles(self):
        self.AccountListWidget.clear()
        self.AccountListWidget.setIconSize(QSize(50, 50))
        for d in [x for x in STORAGE_DIR_PATH.iterdir() if x.is_dir()]:
            file_path = d / 'profile.bin'
            if file_path.is_file():
                with open(file_path, 'rb') as fd:
                    user_info = zwift_user_profile_interpreter(fd.read())

                # download avatar
                with open(d / 'avatar', 'rb') as fp:
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
        if save_or_not and account_dialog.account_dict.get('uid', False):
            try:
                account_dict = account_dialog.account_dict
                p = STORAGE_DIR_PATH / str(account_dict['uid'])
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

        # refresh listwidget
        self.list_profiles()

    @pyqtSlot(bool)
    def on_deleteAccountBtn_clicked(self):
        item = self.AccountListWidget.currentItem()
        if not item:
            return
        logger.info(item.data(Qt.UserRole))
        shutil.rmtree(STORAGE_DIR_PATH / item.data(Qt.UserRole))
        # refresh listwidget
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
        add_cert(zwift_path=self.zwift_path)
        self.edit_host(enable=True)

    @pyqtSlot(bool)
    def on_stopServiceBtn_clicked(self):
        self.stopServiceBtn.setEnabled(False)
        self.startServiceBtn.setEnabled(True)
        self.stop_service()

    @staticmethod
    def start_fake_server():
        t = Thread(target=standalone.start)
        t.daemon = True
        t.start()

    @staticmethod
    def edit_host(enable):
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
        self.edit_host(enable=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())
