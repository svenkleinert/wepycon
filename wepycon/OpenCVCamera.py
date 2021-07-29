import cv2
import numpy as np
import sys

from .AbstractCamera import AbstractCamera

class OpenCVCamera(AbstractCamera):
    def __init__(self, camera_id, px_size=1, resolutions=None):
        self.id = camera_id
        if sys.platform == "win32":
            self.device = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        else:
            self.device = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
            
        print( self.device.getBackendName() )
        self.device.set(cv2.CAP_PROP_FORMAT, -1)

        self.controls_available = {}
        if resolutions is None:
            print("find")
            self.resolutions = self._find_supported_resolutions()
        else:
            self.resolutions = resolutions
        
        self.controls_available["Resolution"] = [list, (["{0:d}x{1:d}".format(res[0], res[1]) for res in self.resolutions], len(self.resolutions) - 1), None]
        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolutions[-1][0])
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolutions[-1][1])

        
        brightness = self.device.get(cv2.CAP_PROP_BRIGHTNESS)
        available = self.device.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        if available:
            self.controls_available["Brightness"] = [int, (0, 100, brightness), cv2.CAP_PROP_BRIGHTNESS]

        contrast = self.device.get(cv2.CAP_PROP_CONTRAST)
        available = self.device.set(cv2.CAP_PROP_CONTRAST, contrast)
        if available:
            self.controls_available["Contrast"] = [int, (0, 100, contrast), cv2.CAP_PROP_CONTRAST]

        saturation = self.device.get(cv2.CAP_PROP_SATURATION)
        available = self.device.set(cv2.CAP_PROP_SATURATION, saturation)
        if available:
            self.controls_available["Saturation"] = [int, (0, 100, saturation), cv2.CAP_PROP_SATURATION]

        hue = self.device.get(cv2.CAP_PROP_HUE)
        available = self.device.set(cv2.CAP_PROP_HUE, hue)
        if available:
            self.controls_available["Hue"] = [int, (0, 100, hue), cv2.CAP_PROP_HUE]

        gain = self.device.get(cv2.CAP_PROP_GAIN)
        available = self.device.set(cv2.CAP_PROP_GAIN, gain)
        if available:
            self.controls_available["Gain"] = [int, (0, 100, gain), cv2.CAP_PROP_GAIN]

        exposure = self.device.get(cv2.CAP_PROP_EXPOSURE)
        available = self.device.set(cv2.CAP_PROP_EXPOSURE, exposure)
        if available:
            self.controls_available["Exposure"] = [int, (-9, -2, exposure), cv2.CAP_PROP_EXPOSURE]

        available = self.device.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        if available:
            self.controls_available["Auto Exposure"] = [bool, False, cv2.CAP_PROP_AUTO_EXPOSURE]

        self._settings = {}
        for name in self.controls_available.keys():
            if self.controls_available[name][0] == int:
                self._settings[name] = self.controls_available[name][1][-1]
            elif self.controls_available[name][0] == bool:
                self._settings[name] = self.controls_available[name][1]
        
        available = self.device.set(cv2.CAP_PROP_AUTO_WB, 0)
        
        self.height = int( self.device.get(cv2.CAP_PROP_FRAME_HEIGHT) )
        self.width = int( self.device.get(cv2.CAP_PROP_FRAME_WIDTH) )
        
        print(self.device.get(cv2.CAP_PROP_ISO_SPEED))
        self.video_mode = True
        self.adc_bits = 8
        self.px_size=px_size

    def get_image(self, timeout=600):
        try:
            success, img = self.device.read()
            if success:
                if img.ndim > 2:
                    img = np.sum(img, axis=2)/3
                return img.astype(np.int)
        except Exception as e:
            print( e )
        return np.zeros((self.height, self.width))

    def _find_supported_resolutions(self):
        candidates = [
                (320, 200),
                (320, 240),
                (352, 288),
                (480, 320),
                (640, 320),
                (768, 576),
                (800, 480),
                (854, 480),
                (1024, 576),
                (1024, 600),
                (1024, 768),
                (1152, 768),
                (1152, 864),
                (1280, 720),
                (1280, 800),
                (1280, 854),
                (1280, 960),
                (1280, 1024),
                (1400, 1050),
                (1440, 1080),
                (1600, 900),
                (1600, 1200),
                (1680, 1050),
                (1920, 1080),
                (1920, 1200),
                (2048, 1080),
                (2048, 1536),
                (2560, 1080),
                (2560, 1440),
                (2560, 1600),
                (2560, 2048),
                (3440, 1440),
                (3840, 2160),
                (4096, 2160),
                ]
        supported_resolutions = []
        initial_resolution = (
            int(self.device.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.device.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )

        for res in candidates:
            self.device.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
            self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])

            w = int(self.device.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.device.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if w == res[0] and h == res[1]:
                supported_resolutions.append(res)

        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, initial_resolution[0])
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, initial_resolution[1])

        return supported_resolutions

    @classmethod
    def list_devices(cls):
        if sys.platform == "win32":
            return scan_camera_windows_dshow()
        elif sys.platform == "linux":
            return scan_camera_linux_v4l2()

    @classmethod
    def from_device_dialog(cls):
        if sys.platform == "win32":
            devices = scan_camera_windows_dshow()
        elif sys.platform == "linux":
            devices = scan_camera_linux_v4l2()
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
    def from_device_number(cls, num, px_size=1, resolutions=None):
        return cls(num, px_size, resolutions)

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings):
        for name, value in settings.items():
            assert name in self._settings.keys()
            self._settings[name] = settings[name]

            _type, _, _id = self.controls_available[name]
            if _id is not None:
                self.device.set(_id, float(value))
            elif name == "Resolution":
                self.device.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolutions[value][0])
                self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolutions[value][1])
                self.width = self.device.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.height = self.device.get(cv2.CAP_PROP_FRAME_HEIGHT)

def scan_camera_linux_v4l2():
    import os
    import v4l2py
    devices = []
    for filename in os.listdir("/dev/"):
        if "video" in filename:
            try:
                info = v4l2py.device.read_info(os.open("/dev/"+filename,os.O_RDWR, os.O_NONBLOCK))
                if info.capabilities.value%2 == 1:
                    _id = int(filename[filename.rfind('o')+1:])
                    devices.append([_id, info.card])
                    print(info)
            except Exception as e:
                print(e)
                pass
    return devices


def scan_camera_windows_dshow():
    from comtypes import client, GUID, IUnknown, COMMETHOD, HRESULT, POINTER, c_ulong, IPersist, c_int, COMError, Structure
    from ctypes.wintypes import _ULARGE_INTEGER, ULONG
    from comtypes.persist import IPropertyBag
    category_clsid = GUID("{860bb310-5d01-11d0-bd3b-00a0c911ce86}")
    system_device_clsid = GUID("{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}")
    
    
    class ISequentialStream(IUnknown):
        _case_insensitive_ = True
        _iid_ = GUID('{0C733A30-2A1C-11CE-ADE5-00AA0044773D}')
        _idlflags_ = []


    class IStream(ISequentialStream):
        _case_insensitive_ = True
        _iid_ = GUID('{0000000C-0000-0000-C000-000000000046}')
        _idlflags_ = []
        
    
    
    
    class IPersistStream(IPersist):
        _case_insensitive_ = True
        _iid_ = GUID('{00000109-0000-0000-C000-000000000046}')
        _idlflags_ = []
        
    IPersistStream._methods_ = [
        COMMETHOD([], HRESULT, 'IsDirty'),
        COMMETHOD([], HRESULT, 'Load',
            (['in'], POINTER(IStream), 'pstm')),
        COMMETHOD([], HRESULT, 'Save',
            (['in'], POINTER(IStream), 'pstm'),
            (['in'], c_int, 'fClearDirty')),
        COMMETHOD([], HRESULT, 'GetSizeMax',
            (['out'], POINTER(_ULARGE_INTEGER), 'pcbSize')),
        ]
    class IBindCtx(IUnknown):
        _case_insensitive_ = True
        _iid_ = GUID("{0000000E-0000-0000-C000-000000000046}")
        _idlflags_ = []
    
    class IMoniker(IPersistStream):
        _case_insensitive_ = True
        _iid_ = GUID("{0000000F-0000-0000-C000-000000000046}")
        _idlflags_ = []
    
    IMoniker._methods_ = [
        COMMETHOD([], HRESULT, "BindToObject",
            (['in'], POINTER(IBindCtx), "pbc"),
            (['in'], POINTER(IMoniker), "pmkToLeft"),
            (['in'], POINTER(GUID), "riidResult"),
            (['out'], POINTER(POINTER(IUnknown)), "ppvResult")),
        COMMETHOD([], HRESULT, "BindToStorage",
            (['in'], POINTER(IBindCtx), "pbc"),
            (['in'], POINTER(IMoniker), "pmkToLeft"),
            (['in'], POINTER(GUID), "riid"),
            (['out'], POINTER(POINTER(IUnknown)), "ppvObj"))
            ]    
        
    class IEnumMoniker(IUnknown):
        _case_insensitive_ = True
        _iid_ = GUID("{00000102-0000-0000-C000-000000000046}")
        _idlflags_ = []
    
    IEnumMoniker._methods_ = [
        COMMETHOD([], HRESULT, "Next",
            (['in'], c_ulong, 'celt'),
            (['out'], POINTER(POINTER(IMoniker)), 'rgelt'),
            (['out'], POINTER(c_ulong), 'pceltFetched')),
        COMMETHOD([], HRESULT, "Skip",
            (['in'], c_ulong, 'celt')),
        COMMETHOD([], HRESULT, "Reset"),
        COMMETHOD([], HRESULT, "Clone",
            (['out'], POINTER(POINTER(IMoniker)), 'ppenum'))
        ]
    
    class iface(IUnknown):
        _iid_ = GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
        _case_insensitive_ = True
        _idflags_ = []
        
    iface._methods_ = [
        COMMETHOD([], HRESULT, "CreateClassEnumerator",
        (["in"], POINTER(GUID), "clsidDeviceClass"),
        (["out"], POINTER(POINTER(IEnumMoniker)), "ppEnumMoniker"),
        (["in"], c_int, "dwFlags"))
    ]
    
    def get_moniker_name(moniker):
        property_bag = moniker.BindToStorage(0, 0, IPropertyBag._iid_).QueryInterface(IPropertyBag)
        print( property_bag )
        return property_bag.Read("FriendlyName", pErrorLog=None)
        
    class CAUUID(Structure):
        _fields_ = (
            ('element_count', ULONG),
            ('elements', POINTER(GUID)),
            )    
    class ISpecifyPropertyPages(IUnknown):
        _case_insensitive_ = True
        _iid_ = GUID('{B196B28B-BAB4-101A-B69C-00AA00341D07}')
        _idlflags_ = []
        _methods_ = [
            COMMETHOD([], HRESULT, 'GetPages',
              (['out'], POINTER(CAUUID), 'pPages'),
              )
            ]
            
            
    def show_properties(object):
        try:
            spec_pages = object.QueryInterface(ISpecifyPropertyPages)
            cauuid = spec_pages.GetPages()
            if cauuid.element_count > 0:
                whandle = windll.user32.GetTopWindow(None)
                OleCreatePropertyFrame(
                    whandle,
                    0, 0, None,
                    1, byref(cast(object, LPUNKNOWN)),
                    cauuid.element_count, cauuid.elements,
                    0, 0, None)
                windll.ole32.CoTaskMemFree(cauuid.elements)
        except COMError:
            pass
    
    device_enum = client.CreateObject(system_device_clsid, interface=iface)
    print( device_enum )
    filter_enum = device_enum.CreateClassEnumerator(category_clsid, dwFlags=0)
    moniker, count = filter_enum.Next(1)
    result = []
    while count > 0:
        print( show_properties(moniker))
        result.append(get_moniker_name(moniker))
        moniker, count = filter_enum.Next(1)
    print( result )
