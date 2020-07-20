from stravalib import Client
from flask import Flask, request
from const import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from PyQt5.QtCore import QObject, pyqtSignal


class Bridge(QObject):
    token_got = pyqtSignal(dict)

    def __init__(self):
        super().__init__(parent=None)


bridge = Bridge()

app = Flask(__name__)


@app.route('/authorization')
def authorization():
    code = request.args.get('code')
    client = Client()
    access_token = client.exchange_code_for_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        code=code
    )
    bridge.token_got.emit(access_token)
    return access_token
