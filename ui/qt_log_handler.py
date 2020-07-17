import logging
from PyQt5.QtCore import pyqtSignal, QObject


class QLogHandler(QObject, logging.Handler):
    newRecord = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        super(logging.Handler).__init__()

        formatter = Formatter('[%(asctime)s][%(levelname)s] -- %(message)s - (%(name)s)', '%d/%m/%Y %H:%M:%S')
        self.setFormatter(formatter)
        self.setLevel(logging.DEBUG)

    def emit(self, record):
        msg = self.format(record)
        self.newRecord.emit(msg)


class Formatter(logging.Formatter):
    def formatException(self, ei):
        result = super(Formatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(Formatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s
