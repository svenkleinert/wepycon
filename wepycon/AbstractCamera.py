from abc import ABC

class AbstractCamera(ABC):
    def __init__(self, *args):
        pass

    def get_image(self, *args):
        raise NotImplementedError("get_image")

    @classmethod
    def from_device_dialog(cls):
        raise NotImplementedError("from_device_dialog")

    @property
    def settings(self):
        raise NotImplementedError("settings")