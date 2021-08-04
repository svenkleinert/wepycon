from . import QWidget, QComboBox, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QGroupBox, Slot, QRadioButton, Signal
from wepycon import camera_types 
from wepycon.AbstractCamera import AbstractCamera


class InitWidget(QWidget):
    camera_opened = Signal(AbstractCamera)
    def __init__(self):
        super(InitWidget, self).__init__()
        vbox = QVBoxLayout()
        self.label = QLabel("Camera:")
        vbox.addWidget(self.label)

        self.camera_type_combo = QComboBox()
        for name in camera_types.keys():
            self.camera_type_combo.addItem(name)
        self.camera_type_combo.currentIndexChanged.connect(self.on_type_changed)
        vbox.addWidget(self.camera_type_combo)

        self.group_box = QGroupBox()
        self.group_box_vbox = QVBoxLayout()
        self.group_box.setLayout(self.group_box_vbox)
        self.on_type_changed()
        vbox.addWidget(self.group_box)

        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.on_open_button)
        vbox.addWidget(self.open_button)

        self.setLayout(vbox)

    @Slot()
    def on_type_changed(self):
        for i in range( self.group_box_vbox.count() ):
            item = self.group_box_vbox.itemAt(0)
            item.widget().hide()
            self.group_box_vbox.removeItem( item )
        
        _type = self.camera_type_combo.currentText()
        devices = camera_types[_type].list_devices()
        if len(devices) == 0:
            self.group_box_vbox.addWidget(QLabel("No device found"))
        else:
            for _id, name in devices:
                self.group_box_vbox.addWidget(QRadioButton(name))


    @Slot()
    def on_open_button(self):
        if self.group_box_vbox.count() > 0:
            if isinstance(self.group_box_vbox.itemAt(0).widget(), QLabel):
                return

            _type = self.camera_type_combo.currentText()
            for i in range( self.group_box_vbox.count() ):
                if self.group_box_vbox.itemAt(i).widget().isChecked():
                    try:
                        self.camera_opened.emit(camera_types[_type].from_device_number(i))
                    except Exception as e:
                        print(e)
