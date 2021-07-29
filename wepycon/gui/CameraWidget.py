from . import QWidget, QLabel, QVBoxLayout, QPushButton, Slot, QHBoxLayout, QFormLayout, QComboBox, QSpinBox, QCheckBox, QGridLayout, QSizePolicy
from .BeamWorker import BeamWorker
from .MatplotlibWidget import MatplotlibWidget
from .BeamWidget import BeamWidget
import numpy as np
import time
from matplotlib import cm

class CameraWidget(QWidget):
    def __init__(self, camera):
        super(CameraWidget, self).__init__()
        self.camera = camera
        self.is_running = False
        

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        self.grid = QGridLayout()
        self.beam_widget = BeamWidget(self.camera)
        self.beam_widget.resize(640, 480)
        self.grid.addWidget(self.beam_widget,0,0)
        self.beam_widget.crosshair_signal.connect(self.set_cross_spin_value)
        self.beam_widget.circle_signal.connect(self.set_circle_spin_value)
        
        self.x_plot_widget = MatplotlibWidget(horizontal=True)
        _x = np.arange(self.camera.width) * self.camera.px_size
        _x = _x - np.mean(_x)
        self.x_plot_widget.plot(_x, np.zeros_like(_x))
        self.x_plot_widget.hide()
        self.x_plot_widget.set_ylim([0, 1])
        self.grid.addWidget(self.x_plot_widget, 1, 0)
        self.y_plot_widget = MatplotlibWidget(horizontal=False)
        _y = np.arange(self.camera.height) * self.camera.px_size
        _y = _y - np.mean(_y)
        self.y_plot_widget.plot(_y, np.zeros_like(_y))
        self.y_plot_widget.hide()
        self.y_plot_widget.set_xlim([1,0])
        self.grid.addWidget(self.y_plot_widget, 0, 1)
        self.grid.setColumnStretch(0, 3)
        self.grid.setColumnStretch(1, 0)
        self.grid.setRowStretch(0, 3)
        self.grid.setRowStretch(1, 0)
        hbox.addLayout(self.grid, stretch=1)
        
        self.cam_settings_form = QFormLayout()

        self.colormap_box = QComboBox()
        self.colormap_box.addItems(["None", "jet", "nipy_spectral", "viridis", "cividis"])
        self.colormap_box.currentIndexChanged.connect(self.on_colormap_changed)
        self.cam_settings_form.addRow("Colormap", self.colormap_box)

        ctrl = self.camera.controls_available

        for name, (_type, _values, _id) in ctrl.items():
            if _type == int:
                widget = QSpinBox()
                widget.setRange(_values[0], _values[1])
                widget.setValue(_values[2])
                widget.valueChanged.connect(self.on_settings_changed)
            elif _type == bool:
                widget = QCheckBox()
                widget.setChecked(_values)
                widget.stateChanged.connect(self.on_settings_changed)
            elif _type == list:
                widget = QComboBox()
                widget.addItems(_values[0])
                widget.setCurrentIndex(_values[1])
                widget.currentIndexChanged.connect(self.on_settings_changed)
            self.cam_settings_form.addRow( name, widget )

        vbox.addLayout(self.cam_settings_form)
        vbox.addSpacing(50)

        self.gui_form = QFormLayout()

        self.slices_checkbox = QCheckBox()
        self.slices_checkbox.stateChanged.connect(self.on_slices_changed)
        self.gui_form.addRow("Slices", self.slices_checkbox)
        self.slice_method_box = None

        self.cross_checkbox = QCheckBox()
        self.cross_checkbox.stateChanged.connect(self.on_cross_changed)
        self.gui_form.addRow("Fixed Crosshair", self.cross_checkbox)
        self.cross_x_spin = None
        self.cross_y_spin = None

        self.circle_checkbox = QCheckBox()
        self.circle_checkbox.stateChanged.connect(self.on_circle_changed)
        self.gui_form.addRow("Fixed Circle", self.circle_checkbox)
        self.circle_x_spin = None
        self.circle_y_spin = None
        self.circle_r_spin = None
        
        vbox.addLayout(self.gui_form)
        vbox.addSpacing(50)


        self.button = QPushButton("Start!")
        self.button.clicked.connect(self.on_button)
        vbox.addWidget(self.button)

        self.cmap = None
        
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.worker = BeamWorker(self.beam_widget, self.camera, self.cmap)
        self.update_fun = lambda img : None
        self.resize(1200, 480)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    @Slot()
    def on_button(self):
        self.is_running = not self.is_running

        if self.is_running:
            self.button.setText("Stop!")
            self.frames = 0
            self.start = time.time()
            self.acquire_image()
        else:
            self.button.setText("Start!")

    def acquire_image(self):
        if self.worker.isRunning():
            return

        self.worker = BeamWorker(self.beam_widget, self.camera, self.cmap, self.update_fun)
        self.worker.finished.connect(self.acquisition_finished)
        self.worker.start()

    def acquisition_finished(self):
        self.frames += 1
        #print( self.frames / (time.time()-self.start) )
        if self.is_running:
            self.acquire_image()

    @Slot()
    def on_colormap_changed(self):
        cmap = self.colormap_box.currentText()
        if cmap == "None":
            self.cmap = None
            return
        
        cmap = cm.get_cmap(cmap)
        self.cmap = cmap(np.arange(2**self.camera.adc_bits) / 2**self.camera.adc_bits, bytes=True)


    def on_settings_changed(self):
        was_running = False
        if self.is_running:
            was_running = True
            self.is_running = False
        
        while self.worker.isRunning():
            pass

        settings = {}
        for i in range(1,self.cam_settings_form.rowCount()):
            _name = self.cam_settings_form.itemAt(i, QFormLayout.LabelRole).widget().text()
            widget = (self.cam_settings_form.itemAt(i, QFormLayout.FieldRole)).widget()
            if isinstance(widget, QSpinBox):
                settings[_name] = widget.value()
            elif isinstance(widget, QCheckBox):
                settings[_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                settings[_name] = widget.currentIndex()
        self.camera.settings = settings

        if was_running:
            self.is_running = True
            self.acquire_image()

    def on_slices_changed(self):
        if self.slices_checkbox.isChecked():
            self.x_plot_widget.show()
            self.y_plot_widget.show()
            self.grid.setColumnStretch(1, 1)
            self.grid.setRowStretch(1, 1)
            if self.slice_method_box is None:
                self.slice_method_box = QComboBox()
                self.slice_method_box.addItems(["Peak", "COG", "integrate"])
                self.slice_method_box.currentIndexChanged.connect(self.on_slices_changed)
                self.gui_form.insertRow(1, "Method", self.slice_method_box)


            if self.slice_method_box.currentText() == "Peak":
                def update_fun(img):
                    ind_y, ind_x = np.unravel_index(np.argmax(img), img.shape)
                    I_x = img[ind_y,:]
                    I_y = img[:,ind_y]
                    self.x_plot_widget.refresh_data(I_x/np.amax(I_x))
                    self.y_plot_widget.refresh_data(I_y/np.amax(I_y))
                    return  ind_x, ind_y

            elif self.slice_method_box.currentText() == "COG":
                def update_fun(img):
                    _x = np.arange( self.camera.width )
                    _y = np.arange( self.camera.height )
                    ind_x = round(np.sum(_x[np.newaxis,:] * img) / np.sum(img))
                    ind_y = round(np.sum(_y[:,np.newaxis] * img) / np.sum(img))
                    I_x = img[ind_y,:]
                    I_y = img[:,ind_y]
                    self.x_plot_widget.refresh_data(I_x/np.amax(I_x))
                    self.y_plot_widget.refresh_data(I_y/np.amax(I_y))
                    return  ind_x, ind_y
            elif self.slice_method_box.currentText() == "integrate":
                def update_fun(img):
                    I_x = np.sum(img, axis=0)
                    I_y = np.sum(img, axis=1)
                    self.x_plot_widget.refresh_data(I_x/np.amax(I_x))
                    self.y_plot_widget.refresh_data(I_y/np.amax(I_y))
                    return None

        else:
            self.x_plot_widget.hide()
            self.y_plot_widget.hide()
            self.grid.setColumnStretch(1, 0)
            self.grid.setRowStretch(1, 0)
            if self.slice_method_box is not None:
                self.gui_form.removeRow(self.slice_method_box)
                self.slice_method_box = None
            update_fun = lambda img : None

        self.update_fun = update_fun

    @Slot()
    def on_cross_changed(self):
        if self.cross_checkbox.isChecked():
            if self.cross_x_spin is None or self.cross_y_spin is None:
                self.cross_x_spin = QSpinBox()
                self.cross_x_spin.setRange(0, self.camera.width)
                self.cross_x_spin.valueChanged.connect(self.on_cross_spin)
                self.cross_y_spin = QSpinBox()
                self.cross_y_spin.setRange(0, self.camera.height)
                self.cross_y_spin.valueChanged.connect(self.on_cross_spin)
                self.set_cross_spin_value()
                idx, _ = self.gui_form.getWidgetPosition(self.cross_checkbox)
                self.gui_form.insertRow(idx+1, "Crosshair x", self.cross_x_spin)
                self.gui_form.insertRow(idx+2, "Crosshair y", self.cross_y_spin)
            self.beam_widget.cross = True
        else:
            self.gui_form.removeRow(self.cross_x_spin)
            self.gui_form.removeRow(self.cross_y_spin)
            self.cross_x_spin = None
            self.cross_y_spin = None
            self.beam_widget.cross = False

    @Slot()
    def on_cross_spin(self):
        _x = self.cross_x_spin.value()
        _y = self.cross_y_spin.value()
        self.beam_widget.cross_location = (_x, _y)

    @Slot()
    def set_cross_spin_value(self):
        if self.cross_x_spin is not None and self.cross_y_spin is not None:
            loc = self.beam_widget.cross_location
            if loc is not None:
                self.cross_x_spin.valueChanged.disconnect(self.on_cross_spin)
                self.cross_y_spin.valueChanged.disconnect(self.on_cross_spin)
                _x = loc[0]
                _y = loc[1]
                self.cross_x_spin.setValue(_x)
                self.cross_y_spin.setValue(_y)
                self.cross_x_spin.valueChanged.connect(self.on_cross_spin)
                self.cross_y_spin.valueChanged.connect(self.on_cross_spin)

    @Slot()
    def on_circle_changed(self):
        if self.circle_checkbox.isChecked():
            if self.circle_x_spin is None or self.circle_y_spin is None:
                self.circle_x_spin = QSpinBox()
                self.circle_x_spin.setRange(0, self.camera.width)
                self.circle_x_spin.valueChanged.connect(self.on_circle_spin)
                self.circle_y_spin = QSpinBox()
                self.circle_y_spin.setRange(0, self.camera.height)
                self.circle_y_spin.valueChanged.connect(self.on_circle_spin)
                self.circle_r_spin = QSpinBox()
                self.circle_r_spin.setRange(0, min(self.camera.height, self.camera.width))
                self.circle_r_spin.valueChanged.connect(self.on_circle_spin)

                self.set_circle_spin_value()

                idx, _ = self.gui_form.getWidgetPosition(self.circle_checkbox)
                self.gui_form.insertRow(idx+1, "Circle x", self.circle_x_spin)
                self.gui_form.insertRow(idx+2, "Circle y", self.circle_y_spin)
                self.gui_form.insertRow(idx+3, "Circle r", self.circle_r_spin)
            self.beam_widget.circle = True
        else:
            self.gui_form.removeRow(self.circle_x_spin)
            self.gui_form.removeRow(self.circle_y_spin)
            self.gui_form.removeRow(self.circle_r_spin)
            self.circle_x_spin = None
            self.circle_y_spin = None
            self.circle_r_spin = None
            self.beam_widget.circle = False

    @Slot()
    def on_circle_spin(self):
        _x = self.circle_x_spin.value()
        _y = self.circle_y_spin.value()
        _r = self.circle_r_spin.value()
        self.beam_widget.circle_location = (_x, _y)
        self.beam_widget.circle_radius = _r


    @Slot()
    def set_circle_spin_value(self):
        if self.circle_x_spin is not None and self.circle_y_spin is not None:
            loc = self.beam_widget.circle_location
            if loc is not None:
                self.circle_x_spin.valueChanged.disconnect(self.on_circle_spin)
                self.circle_y_spin.valueChanged.disconnect(self.on_circle_spin)
                _x = loc[0]
                _y = loc[1]
                self.circle_x_spin.setValue(_x)
                self.circle_y_spin.setValue(_y)
                self.circle_x_spin.valueChanged.connect(self.on_circle_spin)
                self.circle_y_spin.valueChanged.connect(self.on_circle_spin)

            _r = self.beam_widget.circle_radius
            if _r is not None:
                self.circle_r_spin.setValue(_r)
                self.circle_r_spin.valueChanged.connect(self.on_circle_spin)
