import os
import ctypes
import sys
import logging
from subprocess import Popen, PIPE, TimeoutExpired

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QDialog

from protobuf import profile_pb2

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
cwd = os.getcwd()


def is_admin():
    try:
        admin = (os.getuid() == 0)
    except AttributeError:
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return admin


def add_cert(zwift_path='C:/Program Files (x86)/Zwift'):
    logger = logging.getLogger()
    cert_path = os.path.join(bundle_dir, 'ssl', 'cert-zwift-com.p12')
    pem_path = os.path.join(bundle_dir, 'ssl', 'cert-zwift-com.pem')
    zwift_pem_path = os.path.join(zwift_path, 'data', 'cacert.pem')
    logger.info('添加证书')
    logger.info(f'pem:{pem_path}')
    logger.info(f'p12:{cert_path}')
    logger.info(f'zwift:{zwift_pem_path}')

    with Popen(
            ['certutil.exe', '-importpfx', 'Root', cert_path],
            close_fds=True,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True
    ) as proc:
        outs, errs = proc.communicate()
        logger.info(outs)
        logger.error(errs)

    with Popen(
            ['type', pem_path, '>>', zwift_pem_path],
            close_fds=True,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True
    ) as proc:
        outs, errs = proc.communicate()
        logger.info(outs)
        logger.error(errs)

    # 'certutil.exe -importpfx Root cert-zwift-com.p12'

    # 'certutil.exe -importpfx cert-zwift-com.p12'
    # 'type cert-zwift-com.pem >> "C:\Program Files (x86)\Zwift\data\cacert.pem"'


def zwift_user_profile_interpreter(profile_bytes):
    profile_proto = profile_pb2.Profile()

    profile_proto.ParseFromString(profile_bytes)
    print(profile_proto.f58.decode())

    return {
        "first_name": profile_proto.first_name,
        "last_name": profile_proto.last_name,
        "uid": profile_proto.id,
        "avatar": profile_proto.f58.decode()
    }


def FileDialog():
    dialog = QFileDialog()
    foo_dir = dialog.getExistingDirectory(dialog, '选择Zwift的安装目录！')
    return foo_dir
