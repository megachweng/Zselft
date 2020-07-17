from PyQt5.QtWidgets import QDialog
from ui.accountForm import Ui_account


class AddAccountDialog(QDialog, Ui_account):
    def __init__(self, parent=None):
        super(AddAccountDialog, self).__init__(parent=parent)
        self.setupUi(self)
