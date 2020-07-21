import sys
import logging
from bisect import bisect
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel, QDialog, QGridLayout, QDialogButtonBox
from const import STORAGE_DIR_PATH, XP_LEVEL
from protobuf.profile_pb2 import Profile

logger = logging.getLogger('profile_editor')


class ProfileEditor(QDialog):
    def __init__(self, zwift_uid, parent=None):
        super().__init__(parent=parent)
        self.zwift_uid = zwift_uid
        self.profile_bin = STORAGE_DIR_PATH / str(self.zwift_uid) / 'profile.bin'
        self.profile_proto = Profile()
        only_int_validator = QIntValidator(0, 999999999, self)
        layout = QGridLayout(self)
        self.setLayout(layout)
        distance_label = QLabel('骑行里程 (m)', self)
        self.distance_editor = QLineEdit(self)
        self.distance_editor.setValidator(only_int_validator)
        layout.addWidget(distance_label, 0, 0)
        layout.addWidget(self.distance_editor, 0, 1)

        elevation_gain_label = QLabel('爬升里程 (m)', self)
        self.elevation_gain_editor = QLineEdit(self)
        self.elevation_gain_editor.setValidator(only_int_validator)
        layout.addWidget(elevation_gain_label, 1, 0)
        layout.addWidget(self.elevation_gain_editor, 1, 1)

        ride_time_label = QLabel('骑行时间 (min)', self)
        self.ride_time_edit = QLineEdit(self)
        self.ride_time_edit.setValidator(only_int_validator)
        layout.addWidget(ride_time_label, 2, 0)
        layout.addWidget(self.ride_time_edit, 2, 1)

        self.xp_label = QLabel('经验值', self)
        self.xp_edit = QLineEdit(self)
        self.xp_edit.setValidator(only_int_validator)
        layout.addWidget(self.xp_label, 3, 0)
        layout.addWidget(self.xp_edit, 3, 1)

        drops_label = QLabel('汗水', self)
        self.drops_edit = QLineEdit(self)
        self.drops_edit.setValidator(only_int_validator)
        layout.addWidget(drops_label, 4, 0)
        layout.addWidget(self.drops_edit, 4, 1)

        button_box = QDialogButtonBox(self)
        button_box.setStandardButtons(QDialogButtonBox.Close | QDialogButtonBox.Save)
        button_box.setCenterButtons(True)
        layout.addWidget(button_box, 5, 1)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.xp_edit.textChanged.connect(self.xp_to_level)
        self.load_profile()

    def load_profile(self):
        logger.info(f'Find file {self.profile_bin}')
        with open(self.profile_bin, 'rb') as fp:
            self.profile_proto.ParseFromString(fp.read())
        logger.debug(self.profile_proto)
        self.distance_editor.setText(str(self.profile_proto.total_distance_in_meters))
        self.elevation_gain_editor.setText(str(self.profile_proto.elevation_gain_in_meters))
        self.ride_time_edit.setText(str(self.profile_proto.time_ridden_in_minutes))
        self.ride_time_edit.setText(str(self.profile_proto.time_ridden_in_minutes))
        self.xp_edit.setText(str(self.profile_proto.total_xp))
        self.drops_edit.setText(str(self.profile_proto.f47))

    def save_profile(self):
        self.profile_proto.total_distance_in_meters = int(self.distance_editor.text())
        self.profile_proto.elevation_gain_in_meters = int(self.elevation_gain_editor.text())
        self.profile_proto.time_ridden_in_minutes = int(self.ride_time_edit.text())
        self.profile_proto.total_xp = int(self.xp_edit.text())
        self.profile_proto.f47 = int(self.drops_edit.text())
        if self.profile_bin.is_file():
            with open(self.profile_bin, 'wb') as fp:
                fp.write(self.profile_proto.SerializeToString())
                logger.info('Save profile')

    def xp_to_level(self, xp):
        if not xp:
            xp = 0
        level = bisect(XP_LEVEL, int(xp))
        self.xp_label.setText(f'经验值 (等级:{level})')

    def accept(self):
        self.save_profile()
        super(ProfileEditor, self).accept()


if __name__ == '__main__':
    app = QApplication([])
    p = ProfileEditor(1316671)
    p.show()
    sys.exit(app.exec_())
