import distro
from werkflow.modules.system.architecture.types import ArchitectureType
from .base import OperatingSystem
from .types import OperatingSystemType

class Linux(OperatingSystem):

    def __init__(self) -> None:
        super().__init__()

        self.name = distro.id().capitalize()
        self.type = OperatingSystemType.LINUX

        self.supported_architectures = {
            ArchitectureType.ARM_64: 'arm64',
            ArchitectureType.x86_64: 'x86_64',
            ArchitectureType.AMD_64: 'AMD64'
        }
        