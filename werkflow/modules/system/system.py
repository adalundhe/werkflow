import platform
from typing import Dict
from werkflow.modules.base import Module
from .architecture.types import ArchitectureType
from .configuration import Configuration
from .exceptions import (
    UnsupportedArchitectureException,
    UnsupportedOperatingSystemException
)
from .operating_system import (
    Linux,
    MacOS,
    Windows,
    OperatingSystem,
    OperatingSystemType
)
from .users import Users


class System(Module):

    def __init__(self) -> None:
        super().__init__()

        self._supported_operating_systems: Dict[OperatingSystemType, OperatingSystem] = {
            OperatingSystemType.LINUX: Linux,
            OperatingSystemType.MAC_OS: MacOS,
            OperatingSystemType.WINDOWS: Windows
        }

        self._supported_architectures: Dict[str, ArchitectureType] = {
            architecture.value: architecture for architecture in ArchitectureType
        }

        self.users = Users()
        
        operating_system_type = OperatingSystem.detect()
        self.os: OperatingSystem = None

        try:

            self.os: OperatingSystem = self._supported_operating_systems[operating_system_type]()

        except KeyError:
            raise UnsupportedOperatingSystemException(
                list([
                    os_option.value for os_option in self._supported_operating_systems.keys()
                ])
            )
           
        processor_architecture = self._supported_architectures.get(
            platform.machine()
        )
        
        self.architecture = self.os.supported_architectures.get(processor_architecture)

        if self.architecture is None:
            raise UnsupportedArchitectureException(
                self.os.name,
                processor_architecture,
                list(self.os.supported_architectures.values()),
            )
        
        self.configuration = Configuration()
