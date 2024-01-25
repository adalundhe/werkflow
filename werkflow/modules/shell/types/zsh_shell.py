import asyncio
import subprocess
import functools
import pathlib
import os
from concurrent.futures import ThreadPoolExecutor
from werkflow.modules.system import System
from typing import Dict, Union, TextIO, BinaryIO, Optional


class ZSHShell:

    def __init__(self) -> None:
        self.last_command: str = None
        self.env = os.environ.copy()
        system = System()
        self._executor = ThreadPoolExecutor(
            max_workers=system.configuration.cores.physical
        )

        self._loop: asyncio.AbstractEventLoop = None
        self.envfile_name = '.zshrc'
        self.envfile_path = os.path.join(
            system.users.home,
            self.envfile_name
        )

        self.silent = False

    def path_is_file(
        self,
        path: str
    ) -> bool:
        return len(pathlib.Path(path).suffix) > 0
    
    def path_is_directory(
        self,
        path: str
    ) -> bool:
        return len(pathlib.Path(path).suffix) == 0
    
    async def get_envar(
        self,
        envar_name: str
    ) -> Union[str, None]:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                os.getenv,
                envar_name
            )
        )
    
    async def set_envar(
        self,
        envar_name: str,
        envar_value: str
    ):
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                os.putenv,
                envar_name,
                envar_value
            )
        )


    async def check_if_is_file(
        self,
        filepath: str
    ) -> bool:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
            
        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(   
                os.path.isfile,
                filepath
            )
        )
    
    async def check_if_is_directory(
        self,
        filepath: str
    ) -> bool:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
            
        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(   
                os.path.isdir,
                filepath
            )
        )

    async def to_absolute_path(
        self, 
        filepath: str
    ) -> str:

        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        system = System()
        if "~/" == filepath[:2]:
            filepath = os.path.join(
                system.users.home,
                filepath[2:]
            )

        path = pathlib.Path(filepath)
        resolved_path = await self._loop.run_in_executor(
            self._executor,
            path.resolve
        )

        absolute_path = str(resolved_path)

        if filepath[-1] == "/":
            absolute_path = f'{absolute_path}/'
        
        return absolute_path
    
    async def to_relative_path(
        self,
        base_path: str,
        absolute_path: str
    ) -> str:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        relative_path = await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                os.path.relpath,
                absolute_path,
                base_path
            )
        )

        return relative_path.replace('../', '')

    async def get_current_directory(self) -> str:

        if self._loop is None:
            self._loop = asyncio.get_running_loop()
            
        return await self._loop.run_in_executor(
            self._executor,
            os.getcwd
        )

    async def change_directory(
        self,
        directory_path: str
    ) -> None:

        absolute_path = await self.to_absolute_path(directory_path)

        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                os.chdir,
                absolute_path
            )
        )

    async def assume_admin(
        self,
        password: str=None
    ) -> subprocess.CompletedProcess[str]:
        
        output_pipe = subprocess.PIPE if self.silent else None

        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        result = await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                subprocess.run,
                [*f"sudo -S -v".split()],
                stdout=output_pipe, 
                stderr=output_pipe,
                text=True, 
                input=password,
                env={
                    **self.env
                }
            )
        )

        return result

    async def run(self, 
            command: str,
            command_input: str=None,
            path: Optional[str]=None,
            env: Dict[str, str]={},
            as_shell: bool=False
        ) -> subprocess.CompletedProcess[str]:
        
        output_pipe = subprocess.PIPE if self.silent else None
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        process_command = command
        if as_shell is False:
            process_command = [*command.split()]

        self.last_command = command
        result = await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                subprocess.run,
                process_command,
                cwd=path,
                stdout=output_pipe, 
                stderr=output_pipe,
                text=True, 
                input=command_input,
                shell=as_shell,
                env={
                    **self.env,
                    **{
                        key: str(value) for key, value in env.items()
                    }
                }
            )
        )

        return result
    
    async def eval(
        self,
        command: str,
        env: Dict[str, str]={}
    ) -> None:
        await self.run(
            f'eval "$({command})"',
            env=env,
            as_shell=True
        )

    async def copy(
        self,
        source_directory: str,
        destination_directory: str,
        recursive: bool=False
    ) -> None:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        if recursive:
            await self.run(
                f'cp -r {source_directory} {destination_directory}'
            )

        else:
            await self.run(
                f'cp {source_directory} {destination_directory}'
            )
    
    
    async def move(
        self,
        source_directory: str,
        destination_directory: str
    ) -> None:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        await self.run(
            f'mv {source_directory} {destination_directory}',
            as_shell=True
        )
    
    async def append_to_envfile(
        self,
        variable_name: str,
        variable_value: str
    ) -> None:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        environmental_variable = f'export {variable_name}={variable_value}'
        envfile = await self.open_or_create_file(self.envfile_path)

        await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                envfile.write,
                environmental_variable
            )
        )

        await self._loop.run_in_executor(
            self._executor,
            envfile.close
        )

    async def check_path_exists(
        self,
        filepath: str
    ) -> bool:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        
        absolute_path = await self.to_absolute_path(filepath)

        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                os.path.exists,
                absolute_path
            )
        )
    
    async def touch(
        self,
        filepath: str,
        is_bytes: bool=False,
        overwrite: bool=False
    ) -> None:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        absolute_path = await self.to_absolute_path(filepath)

        created_file = await self.create_file(
            absolute_path,
            is_bytes=is_bytes,
            overwrite=overwrite
        )
        
        if created_file:
            await self._loop.run_in_executor(
                self._executor,
                created_file.close
            )

    async def create_file(
        self,
        filepath: str,
        is_bytes: bool=False,
        overwrite: bool=False
    ) -> Union[TextIO, BinaryIO]:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        absolute_path = await self.to_absolute_path(filepath)
        file_exists = await self.check_path_exists(absolute_path)

        write_mode = 'w+'
        if is_bytes:
            write_mode = 'wb+'

        if file_exists is False or overwrite is True:
            return await self._loop.run_in_executor(
                self._executor,
                functools.partial(
                    open,
                    absolute_path,
                    write_mode
                )
            )
        
    async def open_or_create_file(
        self,
        filepath: str,
        is_bytes: bool=False,
        overwrite: bool=False
    ) -> Union[TextIO, BinaryIO]:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        absolute_path = await self.to_absolute_path(filepath)

        write_file = await self.create_file(
            absolute_path,
            is_bytes=is_bytes,
            overwrite=overwrite
        )

        if write_file is None:
            write_file = await self.open_existing_file(
                absolute_path,
                is_bytes=is_bytes,
            )

        return write_file
        
    async def open_existing_file(
        self,
        filepath: str,
        is_bytes: bool=False,
        write_mode: str='a+'
    ) -> Union[TextIO, BinaryIO]:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        if is_bytes and write_mode == 'a+':
            write_mode = 'ab+'

        elif is_bytes and write_mode == 'w+':
            write_mode = 'wb+'

        elif is_bytes and write_mode == 'r':
            write_mode = 'rb'

        absolute_path = await self.to_absolute_path(filepath)

        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                open,
                absolute_path,
                write_mode
            )
        )
    
    async def read_file(      
        self,
        filepath: str,
        is_bytes: bool=False
    ):

        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        absolute_path = await self.to_absolute_path(filepath)

        file_data = await self.open_existing_file(
            absolute_path,
            write_mode='r',
            is_bytes=is_bytes
        )

        data = await self._loop.run_in_executor(
            self._executor,
            file_data.read
        )

        await self._loop.run_in_executor(
            self._executor,
            file_data.close
        )

        return data

    async def pipe_to_file(
        self,
        filepath: str,
        data: Union[str, bytes],
        overwrite: bool=False
    ) -> None:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        
        is_bytes = False
        if isinstance(data, bytes):
            is_bytes = True

        absolute_path = await self.to_absolute_path(filepath)

        write_file = await self.open_or_create_file(
            absolute_path,
            is_bytes=is_bytes,
            overwrite=overwrite
        )

        await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                write_file.write,
                data
            )
        )

        await self._loop.run_in_executor(
            self._executor,
            write_file.close
        )

    async def create_directory(
        self,
        directory_path: str
    ) -> None:
        
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        absolute_path = await self.to_absolute_path(directory_path)

        path_exists = await self.check_path_exists(absolute_path)

        if path_exists is False:
            await self._loop.run_in_executor(
                self._executor,
                functools.partial(
                    os.makedirs,
                    absolute_path
                )
            )

    async def source(self, filepath: str=None) -> None:

        if filepath is None:
            filepath = self.envfile_path

        absolute_path = await self.to_absolute_path(filepath)
        await self.run(
            f'source {absolute_path}',
            as_shell=True
        )

    async def rm(
        self,
        path: str,
        pattern: Optional[str]=None,
        recurse: bool=False
    ) -> None:
        
        absolute_path = await self.to_absolute_path(path)

        path_exists = await self.check_path_exists(absolute_path)

        if pattern is None:
            pattern = '*'

        if recurse and path_exists:
            recurse_path = pathlib.Path(absolute_path)

            matching = await self._loop.run_in_executor(
                self._executor,
                functools.partial(
                    recurse_path.rglob,
                    pattern
                )
            )

            matching_items = [
                str(matching_path) for matching_path in matching
            ]

            if len(matching_items) > 0:
                await asyncio.gather(
                    self._loop.run_in_executor(
                        self._executor,
                        functools.partial(
                            os.remove,
                            matching_path
                        )
                    ) for matching_path in matching_items
                )

        elif path_exists:
            await self._loop.run_in_executor(
                self._executor,
                functools.partial(
                    os.remove,
                    path
                )
            )


    async def close(self) -> None:
        self._executor.shutdown()

    def abort(self):
        self._executor.shutdown()

        