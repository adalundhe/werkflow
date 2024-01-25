from .cpu import CPU
from .drive_group import DriveGroup
from .memory import Memory
from .configuration_summary import ConfigurationSummary


class Configuration:

    def __init__(self) -> None:
        self.cores = CPU()
        self.drives = DriveGroup()
        self.memory = Memory()

    def summary(self) -> ConfigurationSummary:
        return ConfigurationSummary(
            self.cores,
            self.drives,
            self.memory
        )