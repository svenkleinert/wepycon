from abc import ABC
import numpy as np

class AbstractCamera(ABC):
    def __init__(self, *args):
        self.background = None

    def get_image(self, *args):
        raise NotImplementedError("get_image")

    @classmethod
    def from_device_dialog(cls):
        raise NotImplementedError("from_device_dialog")

    @property
    def settings(self):
        raise NotImplementedError("settings")

    def ultracal(self, max_iterations=20, target_mean=-1, target_std=-1):
        #CCD Camera Instrumental Background Estimation Algorithm, Sankowski and Fabijanska
        imgs = np.array([self.get_image(substract_background=False) for i in range(10)])
        background = np.mean(imgs, axis=0)
        mean = abs(np.mean(imgs - background[np.newaxis,:,:]))
        std = np.std(imgs - background[np.newaxis,:,:])
        iterations = 1
        while (mean > target_mean) and (std > target_std) and iterations < max_iterations:
            iterations += 1
            imgs = np.append(imgs, self.get_image(substract_background=False)[np.newaxis,:,:], axis=0)
            background = np.mean(imgs, axis=0)
            mean = abs(np.mean(imgs - background[np.newaxis,:,:]))
            std = np.std(imgs - background[np.newaxis,:,:])
        self.background = background
