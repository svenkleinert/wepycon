import zwoasi as asi
import numpy as np
from .AbstractCamera import AbstractCamera
import os
import platform

if "armv6" in platform.machine():
    lib_filename = os.path.dirname(__file__) + "/lib/armv6/libASICamera2.so.1.18"
elif "armv7" in platform.machine():
    lib_filename = os.path.dirname(__file__) + "/lib/armv7/libASICamera2.so.1.18"
elif "armv8" in platform.machine():
    lib_filename = os.path.dirname(__file__) + "/lib/armv8/libASICamera2.so.1.18"
elif "Linux" == platform.system():
    lib_filename = os.path.dirname(__file__) + "/lib/x64_linux/libASICamera2.so.1.18"
elif "Windows" == platform.system():
    if platform.machine().endswith("64"):
        lib_filename = os.path.dirname(__file__) + "/lib/x64_windows/ASICamera2.dll"
    else:
        lib_filename = os.path.dirname(__file__) + "/lib/x86_windows/ASICamera2.dll"

asi.init(lib_filename)

class ZwoAsiCamera(AbstractCamera):
    def __init__(self, camera_id):
        super(ZwoAsiCamera, self).__init__()
        self.id = camera_id
        self.device = asi.Camera(camera_id)
        
        controls = self.device.get_controls()

        # min bandwidth for stable connection
        if "BandWidth" in controls.keys():
            max_bw = controls["BandWidth"]["MaxValue"]
            self.device.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, max_bw, auto=True)
            del controls["BandWidth"]

        self.controls_available = {}
        for key, value in controls.items():
            if value["IsWritable"] and (not "Auto" in key):
                _min = controls[key]["MinValue"]
                _max = controls[key]["MaxValue"]
                _default = controls[key]["DefaultValue"]
                _id = controls[key]["ControlType"]
                self.controls_available[key] = [int, (_min, _max, _default), _id]

        if "HighSpeedMode" in self.controls_available:
            _, (_, _, _default), _id = self.controls_available["HighSpeedMode"]
            self.controls_available["HighSpeedMode"] = [bool, bool(_default), _id]
        if "HardwareBin" in self.controls_available:
            _, (_, _, _default), _id = self.controls_available["HardwareBin"]
            self.controls_available["HardwareBin"] = [bool, bool(_default), _id]

        self._video_mode = False
        self._adc_bits = 8
        self.device.set_image_type(asi.ASI_IMG_RAW8)
        info = self.device.get_camera_property()
        self.px_size = info["PixelSize"] * 1e-6
        self.width = info["MaxWidth"]
        self.height = info["MaxHeight"]
        self.name = info["Name"]

        if (not info["IsUSB3Host"]) and ("HighSpeedMode" in self.controls_available.keys()):
            del self.controls_available["HighSpeedMode"]
        else:
            self.device.set_control_value( asi.ASI_HIGH_SPEED_MODE, 1 )
            self.controls_available["HighSpeedMode"] = [bool, True, asi.ASI_HIGH_SPEED_MODE]
        
        self.controls_available["VideoMode"] = [bool, True, None]
        self.video_mode = True

        self.controls_available["ADCbits"] = [list, (["8", "16"], 1), None]
        
        self._settings = {}
        for name in self.controls_available.keys():
            _type = self.controls_available[name][0]
            if _type == int:
                self._settings[name] = self.controls_available[name][1][-1]
            elif _type == bool:
                self._settings[name] = self.controls_available[name][1]
            elif _type == list:
                idx = self.controls_available[name][1][1]
                self.settings[name] = self.controls_available[name][1][0][idx]

    @property
    def video_mode(self):
        return self._video_mode
    
    @video_mode.setter
    def video_mode(self, value):
        if value:
            self.device.start_video_capture()
        else:
            self.device.stop_video_capture()
        self._video_mode = value

    @property
    def adc_bits(self):
        return self._adc_bits

    @adc_bits.setter
    def adc_bits(self, value):
        was_video_mode_active = self.video_mode
        self.video_mode = False

        if value > 8:
            self.device.set_image_type(asi.ASI_IMG_RAW16)
            self._adc_bits = 16
        else:
            self.device.set_image_type(asi.ASI_IMG_RAW8)
            self._adc_bits = 8

        if was_video_mode_active:
            self.video_mode = True


    def get_image(self, substract_background=True, timeout=600):
        try:
            if self._video_mode:
                img = self.device.capture_video_frame(timeout=timeout)
            else:
                img = self.device.capture()
            if substract_background and self.background is not None:
                return img - self.background
            return img
        except Exception as e:
            print( e )
            return np.zeros((self.height, self.width), dtype=int)

    @classmethod
    def list_devices(cls):
        devices = asi.list_cameras()
        return list(enumerate(devices))

    @classmethod
    def from_device_dialog(cls):
        devices = asi.list_cameras()
        s = ""
        for i, device in enumerate( devices ):
            s += '\t'
            s += str( i+1 ) + ')'
            s += '\t'
            s += device
            s += '\n'
        decision = int( input( "ZwoAsi Camera:\n" + s) ) - 1
        return cls( decision )

    @classmethod
    def from_device_number(cls, num):
        return cls(num)
    
    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings):
        for name, value in settings.items():
            if not name in self._settings.keys():
                print("WARNING: key", name, "not found!")
                continue
            self._settings[name] = settings[name]
            _type, _, _id = self.controls_available[name]
            if _id is not None:
                self.device.set_control_value(_id, _type(value))
            elif name == "VideoMode":
                self.video_mode = _type(value)
            elif name == "ADCbits":
                self.adc_bits = int(self.controls_available[name][1][0][int(value)])
