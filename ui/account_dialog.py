import os
import pathlib
import requests
import logging
from threading import Thread

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtGui import QDesktopServices
from scripts.get_profile import query_player_profile, login, logout
from scripts import strava_oauth_server
from ui.accountForm import Ui_account
from utls import zwift_user_profile_interpreter
from const import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from stravalib import Client

logger = logging.getLogger()


class AddAccountDialog(QDialog, Ui_account):
    def __init__(self, parent=None):
        super(AddAccountDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.garminPasswordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.zwiftPasswordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.getZwiftProfileBtn.clicked.connect(self.get_zwift_profile)
        self.authStravaBtn.clicked.connect(self.auth_strava)
        self.account_dict = dict()

    def get_zwift_profile(self):
        self.getZwiftProfileBtn.setEnabled(False)

        session = requests.session()
        username = self.zwiftUsernameEdit.text()
        password = self.zwiftPasswordEdit.text()
        if not all([username, password]):
            logger.warning('账号或密码为空')
            self.getZwiftProfileBtn.setEnabled(True)
            return
        try:
            access_token, refresh_token = login(session, username, password)
            profile = query_player_profile(session, access_token)
            logout(session, refresh_token)
            user_info = zwift_user_profile_interpreter(profile)
            self.account_dict['uid'] = user_info['uid']

            if user_info['avatar']:
                rsp = requests.get(user_info['avatar'])
                self.account_dict['avatar'] = rsp.content

            self.account_dict['profile.bin'] = profile


        except Exception as e:
            logger.exception(e)
            self.getZwiftProfileBtn.setEnabled(True)
        else:
            self.getZwiftProfileBtn.setEnabled(False)
            self.getZwiftProfileBtn.setText('获取成功')

    def auth_strava(self):

        if self.account_dict.get('uid', None) is None:
            notify = QMessageBox()
            notify.setText('请先获取Zwift数据！')
            notify.exec_()
            logger.warning('请先获取Zwift数据！')
            return
        strava_oauth_server.bridge.token_got.connect(self.format_strava_token)
        t = Thread(target=strava_oauth_server.app.run, args=('0.0.0.0', 6734))
        t.daemon = True
        t.start()
        client = Client()
        url = client.authorization_url(
            client_id=STRAVA_CLIENT_ID,
            approval_prompt="force",
            scope="activity:write",
            redirect_uri='http://127.0.0.1:6734/authorization')
        QDesktopServices.openUrl(QUrl(url))

    def format_strava_token(self, token_response):

        access_token = token_response['access_token']
        refresh_token = token_response['refresh_token']
        expires_at = token_response['expires_at']

        self.account_dict['strava_token.txt'] = '\n'.join([
            STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, access_token, refresh_token, str(expires_at)
        ])

        self.authStravaBtn.setEnabled(False)
        self.authStravaBtn.setText('授权成功！')
