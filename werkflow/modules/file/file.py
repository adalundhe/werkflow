import asyncio
import functools
import pathlib
from concurrent.futures import ThreadPoolExecutor
from werkflow.modules.base import Module
from werkflow.modules.shell import Shell
from werkflow.modules.system import System
from typing import List


class File(Module):

    def __init__(self) -> None:
        super().__init__()

        self._system = System()
        self._shell = Shell()

        self._loop: asyncio.AbstractEventLoop = None
        self._executor = ThreadPoolExecutor(
            max_workers=self._system.configuration.cores.physical
        )

    async def list_matching_files(
        self,
        path: str,
        pattern: str
    ) -> List[str]:
        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        absolute_path = await self._shell.to_absolute_path(path)

        search_path = pathlib.Path(absolute_path)
        
        results = await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                search_path.rglob,
                pattern
            )
        )

        return [
            str(result) for result in results
        ]
        

    async def close(self):
        await self._shell.close()
        await self._system.close()
        self._executor.shutdown()

    def abort(self):
        self._shell.abort()
        self._system.abort()
        self._executor.shutdown()