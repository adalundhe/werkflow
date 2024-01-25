import platform
import psutil
from typing import Dict
from werkflow.modules.system.architecture.types import ArchitectureType
from .types import OperatingSystemType


class OperatingSystem:

    def __init__(self) -> None:
        self.name: str = None
        self.type: OperatingSystemType = None
        self.version = platform.release()
        self.supported_architectures: Dict[ArchitectureType, str] = {}

    @classmethod
    def detect(cls) -> OperatingSystemType:
        
        if psutil.MACOS:
            return OperatingSystemType.MAC_OS
        
        elif psutil.WINDOWS:
            return OperatingSystemType.WINDOWS
        
        else:
            return OperatingSystemType.LINUX

