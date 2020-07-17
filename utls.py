import os
import ctypes
import sys
import logging
from subprocess import Popen, PIPE, TimeoutExpired

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
    cert_path = os.path.join(bundle_dir,'ssl','cert-zwift-com.p12')
    pem_path = os.path.join(bundle_dir,'ssl','cert-zwift-com.pem')
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

    logger.info('xxxxxxxxxx')

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