import platform
import os
from typing import List, Optional
from werkflow.modules.shell import Shell
from werkflow.modules.base import Module


class Python(Module):

    def __init__(self) -> None:
        super().__init__()

        self.version = platform.python_version()
        self._shell = Shell()

    async def set_python_version(
        self,
        version: str=None,
        skip_if_exists: bool=True,
        force_reinstall: bool=False
    ):
        if version is None:
            version = self.version

        pyenv_install_command = f'pyenv install {version}'

        if skip_if_exists:
            pyenv_install_command = f'pyenv install -s {version}'

        if force_reinstall:
            pyenv_install_command = f'pyenv install -f {version}'

        await self._shell.run(
            pyenv_install_command, 
            silent=True
        )

        await self._shell.run(
            f'pyenv global {version}', 
            silent=True
        )

        await self._shell.eval('pyenv init -')

    async def create_venv(
        self, 
        environment_name: str
    ) -> str:

        absolute_path = await self._shell.to_absolute_path(environment_name)
        await self._shell.run(
            f'python -m venv {absolute_path}',
            silent=True
        )

        return os.path.join(
            absolute_path,
            'bin',
            'activate'
        )

    async def install_requirements(
        self,
        requirements: List[str],
        virtual_environment: str=None
    ) -> None:
        python_requirements = ','.join(requirements)

        if virtual_environment:
            virtual_environment_path = await self._shell.to_absolute_path(
                virtual_environment
            )

            await self._shell.run(
                f'source {virtual_environment_path} && pip install {python_requirements}',
                as_shell=True,
                silent=True
            )

        else:  
            await self._shell.run(
                f'pip install {python_requirements}',
                silent=True
            )

    async def install_requirements_from_file(
        self,
        install_requirements: Optional[List[str]]=None,
        filepath: str='requirements.txt',
        virtual_environment: str=None
    ) -> None:
        
        if install_requirements and len(install_requirements) > 0:

            requirements = '\n'.join(install_requirements)

            await self._shell.pipe_to_file(
                filepath,
                requirements,
                silent=True
            )

        else:
            await self._shell.touch(
                filepath,
                silent=True
            )

        if virtual_environment:

            virtual_environment_path = await self._shell.to_absolute_path(virtual_environment)

            return await self._shell.run(
                f'source {virtual_environment_path} && pip install -r {filepath}',
                as_shell=True,
                silent=True
            )
        
        else:

            return await self._shell.run(
                f'pip install -r {filepath}',
                silent=True
            )

    async def activate_virtual_environment(
        self,
        virtual_envrionment_path: str
    ) -> str:
        python_venv_absolute_location = await self._shell.to_absolute_path(virtual_envrionment_path)
        python_venv_activate_location = os.path.join(
            python_venv_absolute_location,
            'bin',
            'activate'
        )

        await self._shell.source(
            filepath=python_venv_activate_location
        )

        return python_venv_activate_location
    
    async def close(self):
        await self._shell.close()

    def abort(self):
        self._shell.abort()
        
    