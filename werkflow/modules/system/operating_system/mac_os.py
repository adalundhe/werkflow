import platform
from werkflow.modules.system.architecture.types import ArchitectureType
from .base import OperatingSystem
from .types import OperatingSystemType

class MacOS(OperatingSystem):

    def __init__(self) -> None:
        super().__init__()

        self.name = 'MacOS'
        self.type = OperatingSystemType.MAC_OS

        self.supported_architectures = {
            ArchitectureType.ARM_64: 'arm64',
            ArchitectureType.x86_64: 'x86_64'
        }
    
        mac_os_version, _, _ = platform.mac_ver()
        
        self.version = mac_os_version
