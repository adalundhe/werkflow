import os
import psutil
from getpass import getuser
from typing import Iterable
from pathlib import Path


class Users:

    def __init__(self) -> None:
                
        self._system_users = psutil.users()
        
        self.current_user = getuser()
        if self.current_user is None:
            self.current_user = os.getlogin()

        self.home= Path.home()

    def list(self) -> Iterable[str]:
        for user in self._system_users:
            if user.name.startswith('_') is False:
                yield user