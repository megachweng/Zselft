import pathlib
import sys
import os

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    BUNDLE_DIR = sys._MEIPASS
else:
    # we are running in a normal Python environment
    BUNDLE_DIR = pathlib.Path(__file__).parent.absolute()

CWD = pathlib.Path.cwd()
STORAGE_DIR_PATH = CWD / 'storage'
CONFIG_FILE = STORAGE_DIR_PATH / 'config.json'
LATEST_TESTED_ZWIFT_VERSION = '1.0.53342'
STRAVA_APP_CLIENT_ID = 38447
STRAVA_APP_CLIENT_SERCRET = '200ba7fe60c8a1b9a53f7315abd025c945810b37'
STRAVA_CLIENT_ID = '28117'
STRAVA_CLIENT_SECRET = '41b7b7b76d8cfc5dc12ad5f020adfea17da35468'
