from .AbstractCamera import AbstractCamera
import time
import numpy as np

class DebugCamera(AbstractCamera):
    def __init__(self, *args, **kwargs):
        print("[DebugCamera].__init__()")
        self.controls_available = {
            "Exposure": [int, [-9, -1, -2], 0],
            "Gain": [int, [0, 100, 10], 1],
            "Brightness": [int, [0, 100, 20], 2],
            "Hue": [int, [0, 100, 30], 3],
            "Contrast": [int, [0, 100, 40], 4],
            "AutoExposure": [bool, False, 5]
                }
        self.width = 640
        self.height = 480
        self.adc_bits = 8
        self.px_size = 1.0

    def get_image(self, *args, **kwargs):
        #print("[DebugCamera].get_image()")
        time.sleep(0.001)
        x = np.arange(self.width)
        y = np.arange(self.height)
        noise = 0.1
        img = np.exp( -(x[np.newaxis,:]-self.width/2)**2/2/(self.width/10)**2) * np.exp( -(y[:,np.newaxis]-self.height/2)**2/2/(self.width/10)**2) * int(255 * (1-noise))
        img += np.random.random_integers(0, int(255*noise), (self.height, self.width))
        return img.astype(int)

    def apply_settings(self, settings, *args, **kwargs):
        print("[DebugCamera].apply_settings()")

    @classmethod
    def from_device_dialog(cls):
        s = ""
        s += '\t'
        s += str( 1 ) + ')'
        s += '\t'
        s += "DebugCamera"
        s += '\n'
        decision = int( input( "Debug Camera:\n" + s) ) - 1
        return cls( decision )

    @classmethod
    def list_devices(cls):
        return [(0,"DebugCamera")]

    @classmethod
    def from_device_number(cls, num):
        return cls(num)
