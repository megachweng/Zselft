import sys
import os

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
cwd = os.getcwd()
STORAGE_PATH = os.path.join(cwd, 'storage')
STRAVA_CLIENT_ID = '28117'
STRAVA_CLIENT_SECRET = '41b7b7b76d8cfc5dc12ad5f020adfea17da35468'
LATEST_TESTED_ZWIFT_VERSION = '1.0.53342'
