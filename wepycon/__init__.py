camera_types = {}
try:
    from .LogitechC500Camera import LogitechC500Camera
    camera_types[LogitechC500Camera.__name__] = LogitechC500Camera
except ImportError as e:
    print( e )

try:
    from .OpenCVCamera import OpenCVCamera
    camera_types[OpenCVCamera.__name__] = OpenCVCamera
except ImportError as e:
    print( e )

try:
    from .ZwoAsiCamera import ZwoAsiCamera
    camera_types[ZwoAsiCamera.__name__] = ZwoAsiCamera
except ImportError as e:
    print( e )

try:
    from .DebugCamera import DebugCamera
    camera_types[DebugCamera.__name__] = DebugCamera
except ImportError as e:
    print( e )
