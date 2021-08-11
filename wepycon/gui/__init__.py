

USE_PYQT5 = True

if USE_PYQT5:
    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QFormLayout, QComboBox, QSpinBox, QCheckBox, QGridLayout, QSizePolicy, QDialog, QGroupBox, QRadioButton, QTabWidget, QMessageBox
    from PyQt5.QtCore import QThread, pyqtSlot as Slot, Qt, QObject, pyqtSignal as Signal, QSize
    from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
else:
    pass

