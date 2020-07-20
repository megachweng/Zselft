import pathlib
import sys
import os

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    BUNDLE_DIR = pathlib.Path(sys._MEIPASS)
else:
    # we are running in a normal Python environment
    BUNDLE_DIR = pathlib.Path(__file__).parent.absolute()

CWD = pathlib.Path.cwd()
STORAGE_DIR_PATH = CWD / 'storage'
CONFIG_FILE = STORAGE_DIR_PATH / 'config.json'
LATEST_TESTED_ZWIFT_VERSION = '1.0.53342'
STRAVA_CLIENT_ID = '38447'
STRAVA_CLIENT_SECRET = '200ba7fe60c8a1b9a53f7315abd025c945810b37'
