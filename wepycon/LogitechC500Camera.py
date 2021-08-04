import cv2
import numpy as np
import sys

from .OpenCVCamera import OpenCVCamera

class LogitechC500Camera(OpenCVCamera):
    def __init__(self, camera_id):
        res = [
                (160, 120),
                (176, 144),
                (320, 240),
                (352, 288),
                (640, 360),
                (640, 400),
                (640, 480),
                (800, 600),
                (960, 720),
                (1280, 720),
                (1280, 800),
                (1280, 1024),
                ]

        super(LogitechC500Camera, self).__init__(camera_id, px_size=2.8, resolutions=res)

    @classmethod
    def list_devices(cls):
        devices = OpenCVCamera.list_devices()
        return devices

    @classmethod
    def from_device_dialog(cls):
        devices = cls.list_devices()
        s = ""
        for i, device in enumerate( devices ):
            s += '\t'
            s += str( i+1 ) + ')'
            s += '\t'
            s += device[1]
            s += '\n'
        decision = int( input( "OpenCV Camera:\n" + s) ) - 1
        print( devices[decision][0] )
        return cls( devices[decision][0] )

    @classmethod
    def from_device_number(cls, num):
        return cls(num)
