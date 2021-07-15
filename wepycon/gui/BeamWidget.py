from . import QLabel, QImage, QPixmap, Qt, Slot, Signal, QPainter, QColor, QPen, QSize
import numpy as np

class BeamWidget(QLabel):
    crosshair_signal = Signal()
    circle_signal = Signal()
    def __init__(self, camera):
        super(BeamWidget, self).__init__()
        self.camera = camera
        self.cross = False
        self.cross_location = None
        
        self.circle = False
        self.circle_location = None
        self.circle_radius = 0

        self.mouse_pressed = False
        self.mouse_pressed_position = (0, 0)
        self.mouse_move_position = (0, 0)
        self.ROI = [(0, self.camera.width), (0, self.camera.height)]
        self.ROI_width = self.camera.width
        self.ROI_height = self.camera.height

        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.pxmap = QPixmap()
        self.painter = QPainter()
        self.pen = QPen()
        self.pen.setWidth(3)
        self.pen.setColor(QColor(255,255,255,255))
        self.setMinimumSize(10,10)


    def update_image(self, img, depth):
        if img.ndim > 2:
            img = img[self.ROI[1][0]:self.ROI[1][1], self.ROI[0][0]:self.ROI[0][1], ...]
            qim = QImage(img.astype(np.uint8), img.shape[1], img.shape[0], QImage.Format_RGBA8888)
        else:
            img = img[self.ROI[1][0]:self.ROI[1][1], self.ROI[0][0]:self.ROI[0][1]]
            if depth > 8:
                qim = QImage(img.astype(np.uint16), img.shape[1], img.shape[0], QImage.Format_Grayscale16)
            else:
                qim = QImage(img.astype(np.uint8), img.shape[1], img.shape[0], QImage.Format_Grayscale8)

        self.pxmap.convertFromImage(qim)
        if self.cross_location is not None and self.cross:
            _x, _y = self.cross_location
            self.painter.begin(self.pxmap)
            self.painter.setPen(self.pen)
            if _x > self.ROI[0][0] and _x < self.ROI[0][1]:
                _x -= self.ROI[0][0]
                self.painter.drawLine(_x, 0, _x, self.pxmap.height())
            if _y > self.ROI[1][0] and _y < self.ROI[1][1]:
                _y -= self.ROI[1][0]
                self.painter.drawLine(0, _y, self.pxmap.width(), _y)
            self.painter.end()

        if self.circle_location is not None and self.circle_radius is not None and self.circle:
            if self.circle_radius > 2:
                _x, _y = self.circle_location
                _x -= self.ROI[0][0]
                _y -= self.ROI[1][0]
                _r = self.circle_radius
                self.painter.begin(self.pxmap)
                self.painter.setPen(self.pen)
                self.painter.drawEllipse(_x - _r/2, _y - _r/2, _r, _r)
                self.painter.end()

        if self.mouse_pressed:
            _x1, _y1 = self.mouse_pressed_position
            _x2, _y2 = self.mouse_move_position
            _x1 -= self.ROI[0][0]
            _y1 -= self.ROI[1][0]
            _x2 -= self.ROI[0][0]
            _y2 -= self.ROI[1][0]
            self.painter.begin(self.pxmap)
            self.painter.setPen(self.pen)
            self.painter.drawRect(_x1, _y1, _x2 - _x1, _y2 - _y1)
            self.painter.end()

        self.pxmap = self.pxmap.scaled(self.size(), Qt.KeepAspectRatio)
        self.setPixmap(self.pxmap)

    @Slot()
    def mousePressEvent(self, event):
        _x, _y = self._to_camera_coordinates((event.x(), event.y()))
        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.NoModifier:
                self.mouse_pressed = True
                self.mouse_pressed_position = (_x, _y)
                self.mouse_move_position = (_x, _y)
            elif event.modifiers() == Qt.ControlModifier:
                self.cross_location = (_x, _y)
                self.crosshair_signal.emit()
            elif event.modifiers() == Qt.ShiftModifier:
                self.circle_location = (_x, _y)
                self.circle_signal.emit()
        elif event.button() == Qt.RightButton:
            self.ROI = [(0, self.camera.width), (0, self.camera.height)]
            self.ROI_width = self.camera.width
            self.ROI_height = self.camera.height

    @Slot()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            _x2, _y2 = self._to_camera_coordinates((event.x(), event.y()))
            _x1, _y1 = self.mouse_pressed_position
            if abs(_x1 - _x2) > 10 and abs(_y1 - _y2) > 10:
                self.ROI = [sorted((_x1, _x2)), sorted((_y1, _y2))]
                self.ROI_width = self.ROI[0][1] - self.ROI[0][0]
                self.ROI_height = self.ROI[1][1] - self.ROI[1][0]


    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            _x, _y = self._to_camera_coordinates((event.x(), event.y()))
            self.mouse_move_position = (_x, _y)

    @Slot()
    def wheelEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            self.circle_radius += event.angleDelta().y() / 12
            self.circle_radius = min(max(self.circle_radius, 0), self.pxmap.width())
            self.circle_signal.emit()
    
    def _to_camera_coordinates(self, point):
        _x = round(self.ROI[0][0] + point[0] / self.pxmap.width() * self.ROI_width)
        _y = round(self.ROI[1][0] + point[1] / self.pxmap.height() * self.ROI_height)
        _x = min(max(_x, self.ROI[0][0]), self.ROI[0][1])
        _y = min(max(_y, self.ROI[1][0]), self.ROI[1][1])
        return _x, _y

    def sizeHint(self):
        width = self.ROI[0][1] - self.ROI[0][0]
        height = self.ROI[1][1] - self.ROI[1][0]
        return QSize(width, height)
