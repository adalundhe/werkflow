import psutil
from typing import Iterator, Union, Dict
from werkflow.modules.system.exceptions import MissingVolumeException
from .drive import Drive


class DriveGroup:

    def __init__(self) -> None:
        drives = psutil.disk_partitions()

        self._drives: Dict[str, Drive] = {
            drive.device: Drive(drive) for drive in drives
        }

    def __iter__(self) -> Iterator[Drive]:
        for drive in self._drives.values():
            yield drive

    def list(self) -> Iterator[str]:
        for drive_name in self._drives.keys():
            yield drive_name

    def __getitem__(self, drive_name) -> Drive:
        return self.get(drive_name)

    def get(self, drive_name: str) -> Drive:
        drive = self._drives.get(drive_name)
        if drive is None:
            raise MissingVolumeException(
                list(self._drives.keys())
            )
        
        return drive
    
    def exists(self, drive_name: str) -> bool:
        return self._drives.get(drive_name) is not None
    
    def all_like(self, search_drive_name: str) -> Iterator[Drive]:
        for drive_name, drive in self._drives.items():
            if search_drive_name in drive_name:
                yield drive
    
    def like(self, search_drive_name: str) -> Union[Drive, None]:

        for drive_name, drive in self._drives.items():
            if search_drive_name in drive_name:
                return drive
            
        return None
    
    def update(self) -> None:
        drives = psutil.disk_partitions()

        for drive in drives:
            if self._drives.get(drive.device) is None:
                self._drives[drive.device] = Drive(drive)

        for drive in self._drives.values():
            drive.update()

    def at_path(self, path: str) -> Drive:
        for drive in self._drives.values():
            if path == drive.path:
                return drive
            
        raise MissingVolumeException(
            list(self._drives.keys())
        )
    
    def at_path_like(self, path: str) -> Iterator[Drive]:
        for drive in self._drives.values():
            if path in drive.path:
                yield drive

    


