from . import QThread
from matplotlib import cm
import numpy as np

class BeamWorker(QThread):
    def __init__(self, beam_widget, camera, cmap, 
            update_fun=lambda img : None):
        super(BeamWorker, self).__init__()
        self.beam_widget = beam_widget
        self.camera = camera
        self.cmap = cmap
        self.update_fun = update_fun

    def run(self):
        img = self.camera.get_image()
        idxs = self.update_fun(img)
        if idxs is not None:
            img[:,idxs[0]] = 2**self.camera.adc_bits - 1
            img[idxs[1],:] = 2**self.camera.adc_bits - 1 

        if self.cmap is not None:
            img = np.take(self.cmap, np.clip(img.astype(int), 0, 2**self.camera.adc_bits - 1), axis=0)

        self.beam_widget.update_image(img, self.camera.adc_bits)
