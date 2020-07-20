import ctypes
import pathlib
import logging
from subprocess import Popen, PIPE
from PyQt5.QtWidgets import QFileDialog
from protobuf import profile_pb2
from const import BUNDLE_DIR


def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def add_cert(zwift_path: pathlib.Path):
    logger = logging.getLogger()
    cert_path = BUNDLE_DIR / 'ssl/cert-zwift-com.p12'
    pem_path = BUNDLE_DIR / 'ssl/cert-zwift-com.pem'
    zwift_pem_path = zwift_path / 'data/cacert.pem'
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


def choose_zwift_path(path: pathlib.Path):
    if not (path / 'data/cacert.pem').is_file():
        dialog = QFileDialog()
        choose_path = pathlib.Path(dialog.getExistingDirectory(dialog, '选择Zwift的安装目录！'))
        choose_zwift_path(choose_path)
    else:
        return path
