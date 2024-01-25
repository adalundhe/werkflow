from werkflow.modules.system.architecture.types import ArchitectureType
from .base import OperatingSystem
from .types import OperatingSystemType

class Windows(OperatingSystem):

    def __init__(self) -> None:
        super().__init__()

        self.name = 'Windows'
        self.type = OperatingSystemType.WINDOWS

        self.supported_architectures = {
            ArchitectureType.x86_64: 'x86_64',
            ArchitectureType.AMD_64: 'AMD64'
        }
