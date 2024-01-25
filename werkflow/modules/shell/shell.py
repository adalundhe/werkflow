from typing import Dict, Union, Optional
from werkflow.modules.system import System
from werkflow.modules.system.operating_system import OperatingSystemType
from werkflow.modules.base import Module
from .types import ZSHShell


class Shell(Module):

    def __init__(self) -> None:
        super().__init__()
        system = System()

        self._shell_types = {
            OperatingSystemType.MAC_OS: ZSHShell
        }

        self._shell = self._shell_types.get(
            system.os.type,
            ZSHShell
        )()

    def path_is_file(
        self,
        path: str
    ):
        return self._shell.path_is_file(path)
    
    def path_is_directory(
        self,
        path: str
    ):
        return self._shell.path_is_directory(path)
    
    async def get_envar(
        self,
        envar_name: str
    ):
        return await self._shell.get_envar(envar_name)
    
    async def set_envar(
        self,
        envar_name: str,
        envar_value: str
    ):
        await self._shell.set_envar(
            envar_name,
            envar_value
        )

    async def check_if_is_file(
        self,
        path: str
    ):
        return await self._shell.check_if_is_file(path)
    
    async def check_if_is_directory(
        self,
        path: str
    ):
        return await self._shell.check_if_is_directory(path)

    async def get_current_directory(self):
        return await self._shell.get_current_directory()

    async def to_absolute_path(
        self,
        filepath: str
    ):
        return await self._shell.to_absolute_path(
            filepath
        )
    
    async def to_relative_path(
        self,
        base_path: str,
        absolute_path: str
    ):
        return await self._shell.to_relative_path(
            base_path,
            absolute_path
        )
    
    async def change_directory(
        self,
        path: str
    ):
        await self._shell.change_directory(path)

    async def assume_admin(
        self, 
        password: str,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.assume_admin(password=password)
    
    async def run(
        self, 
        command: str, 
        command_input: str=None, 
        path: Optional[str]=None,
        env: Dict[str, str]={},
        as_shell: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.run(
            command,
            command_input=command_input,
            path=path,
            env=env,
            as_shell=as_shell
        )
    
    async def copy(
        self,
        source_directory: str,
        destination_directory: str,
        recursive: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        await self._shell.copy(
            source_directory,
            destination_directory,
            recursive=recursive
        )
    
    async def move(
        self,
        source_directory: str,
        destination_directory: str,
        silent: bool=False
    ):
        self._shell.silent = silent
        await self._shell.move(
            source_directory,
            destination_directory
        )
    
    async def eval(
        self,
        command: str,
        env: Dict[str, str]={},
        silent: bool=False
    ) -> None:
        self._shell.silent = silent
        await self._shell.eval(
            command,
            env=env
        )
    
    async def touch(
        self,
        filepath: str,
        overwrite: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        await self._shell.touch(
            filepath,
            overwrite=overwrite
        )
    
    async def append_to_envfile(
        self,
        variable_name: str,
        variable_value: str,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.append_to_envfile(
            variable_name,
            variable_value
        )
    
    async def check_path_exists(
        self,
        filepath: str,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.check_path_exists(filepath)
    
    async def create_file(
        self,
        filepath: str,
        overwrite: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.create_file(
            filepath,
            overwrite=overwrite
        )
    
    async def open_or_create_file(
        self,
        filepath: str,
        overwrite: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.open_or_create_file(
            filepath,
            overwrite=overwrite
        )
    
    async def open_existing_file(
        self, 
        filepath: str,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.open_existing_file(filepath)
    
    async def pipe_to_file(
        self,
        filepath: str,
        data: Union[str, bytes],
        overwrite: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.pipe_to_file(
            filepath,
            data,
            overwrite=overwrite
        )
    
    async def read_file(
            self,
            filepath: str,
            silent: bool=False
    ) -> str:
        self._shell.silent = silent
        return await self._shell.read_file(
            filepath
        )
    
    async def read_file_as_bytes(
        self,
        filepath: str,
        silent: bool=False
    ) -> bytes:
        self._shell.silent = silent
        return await self._shell.read_file(
            filepath,
            is_bytes=True
        )
    
    async def create_directory(
        self,
        path: str
    ):
        return await self._shell.create_directory(path)
    
    async def source(
        self,
        filepath: str=None,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.source(
            filepath=filepath
        )
    
    async def rm(
        self,
        path: str,
        pattern: Optional[str]=None,
        recurse: bool=False,
        silent: bool=False
    ):
        self._shell.silent = silent
        return await self._shell.rm(
            path,
            pattern=pattern,
            recurse=recurse
        )
    
    async def close(self):
        await self._shell.close()

    def abort(self):
        self._shell.abort()
