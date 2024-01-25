import psutil
from psutil._common import sdiskpart
from .data_amount import DataAmount


class Drive:

    def __init__(self, drive_stats: sdiskpart) -> None:
        self.path = drive_stats.mountpoint
        self.name = drive_stats.device
        self.type = drive_stats.fstype
        self.options = drive_stats.opts

        disk_usage = psutil.disk_usage(self.path)

        self.total = DataAmount(disk_usage.total)
        self.used = DataAmount(disk_usage.used)
        self.available = DataAmount(disk_usage.free)
        self.percentage_used = disk_usage.percent

    @property
    def mounted(self) -> bool:
        return self.path is not None

    def update(self):
        disk_usage = psutil.disk_usage(self.path)

        self.used = DataAmount(disk_usage.used)
        self.available = DataAmount(disk_usage.free)
        self.percentage_used = disk_usage.percent

    @property
    def current_percentage_used(self):
        self.update()
        return self.percentage_used
    
    @property
    def current_available(self):
        self.update()
        return self.available
    
    @property
    def current_used(self):
        self.update()
        return self.used
        