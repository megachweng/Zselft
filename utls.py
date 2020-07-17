import os
import ctypes


def is_admin():
    try:
        admin = (os.getuid() == 0)
    except AttributeError:
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return admin
