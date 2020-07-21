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
XP_LEVEL = [
    0, 1000, 2000, 3000, 4000, 5000, 7000, 10000, 13000, 16000, 19000, 23000, 28000, 33000, 38000, 44000, 50000,
    56000, 62000, 70000, 78000, 88000, 94000, 100000, 110000, 121000, 130000, 140000, 150000, 170000, 180000,
    190000, 200000, 220000, 230000, 250000, 260000, 280000, 290000, 310000, 330000, 340000, 360000, 380000,
    400000, 420000, 440000, 460000, 480000, 500000
]
