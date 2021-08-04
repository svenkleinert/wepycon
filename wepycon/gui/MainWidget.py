from . import QTabWidget, QWidget, Slot, QVBoxLayout
#from .InitDialog import InitDialog
from .InitWidget import InitWidget
from .CameraWidget import CameraWidget

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        vbox = QVBoxLayout()
        self.tab_widget = QTabWidget()
        #self.tab_widget.addTab(QWidget(), "+")
        self.init_widget = InitWidget()
        self.tab_widget.addTab(self.init_widget, "+")
        self.init_widget.camera_opened.connect(self.add_new_camera)
        #self.tab_widget.currentChanged.connect(self.on_tab_changed)
        #self.tab_widget.tabBarClicked.connect(self.on_tab_changed)
        #self.tab_widget.setCornerWidget(QWidget())
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        vbox.addWidget(self.tab_widget)

        self.setMinimumSize(1024, 700)
        self.setLayout(vbox)

    def add_new_camera(self, camera):
        _camera_widget = CameraWidget(camera)
        idx = self.tab_widget.count() - 1 
        self.tab_widget.insertTab(idx, _camera_widget, str(camera))
        self.tab_widget.setCurrentIndex(idx)
