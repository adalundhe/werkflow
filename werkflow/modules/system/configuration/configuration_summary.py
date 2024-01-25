from typing import Dict, List, Union
from .cpu import CPU
from .drive_group import DriveGroup
from .memory import Memory

CPUStats = Dict[str, Union[int, float]]
MemoryStats = Dict[str, Union[int, float]]
DiskStats = List[Dict[str, Union[str, int, float]]]

ConfigurationSummaryDict = Dict[str, Union[CPUStats, MemoryStats, DiskStats]]

class ConfigurationSummary:

    def __init__(
        self,
        cpu: CPU,
        drives: DriveGroup,
        memory: Memory
    ) -> None:
        
        cpu.update()
        self.cpu = {
            'cpu_physical': cpu.physical,
            'cpu_total': cpu.total,
            'cpu_percentage_used': cpu.percentage_used
        }

        memory.update()
        self.memory = {
            'memory_total_mb': memory.total.mb,
            'memory_used_mb': memory.used.mb,
            'memory_available_mb': memory.available.mb,
            'memory_percentage_used': memory.percentage_used
        }

        drives.update()
        self.drives = [
            {
                'drive_name': drive.name,
                'drive_path': drive.path,
                'drive_options': drive.options,
                'drive_total_mb': drive.total.mb,
                'drive_used_mb': drive.used.mb,
                'drive_available_mb': drive.available.mb,
                'drive_percentage_used': drive.percentage_used

            } for drive in drives
        ]

    def to_dict(self) -> ConfigurationSummaryDict:
        return {
            'cpu': self.cpu,
            'memory': self.memory,
            'drives': self.drives
        }