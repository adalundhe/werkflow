import asyncio
import orjson
from collections import deque
from typing import (
    Callable, 
    Coroutine, 
    Any, 
    Tuple, 
    List, 
    Deque,
    Union,
    Dict,
    Optional
)
from werkflow.modules import (
    File,
    Shell,
    System
)
from werkflow.logging import WerkflowLogger
from .exceptions import StepTimeoutError

class Workflow:
    priority=1

    def __init__(self) -> None: 
        self.file = File()
        self.system = System()
        self.shell = Shell()

        self.pending: Deque[asyncio.Task] = deque()
        self.logger = WerkflowLogger()
        self.logger.initialize()
        self.werkflow_config: Dict[str, Any] = {}

    def get_project_option(
        self,
        option_name: str
    ): 
        options: Dict[str, Any] = self.werkflow_config.get('project_options')
        return options.get(option_name)

    async def update_project_options(
        self,
        option_name: str,
        data: Any
    ):
        options: Dict[str, Any] = dict(self.werkflow_config.get('project_options'))
        options[option_name] = data

        self.werkflow_config['project_options'] = options

        path: str = self.werkflow_config.get('config_path')
        
        current_config: str = await self.shell.read_file(
            path,
            silent=True
        )

        current_config: Dict[str, Any] = orjson.loads(current_config)
        current_config.update(self.werkflow_config)

        await self.shell.pipe_to_file(
            path,
            orjson.dumps(
                current_config,
                option=orjson.OPT_INDENT_2
            ).decode(),
            overwrite=True,
            silent=True
        )

    async def as_async(
        self,
        call: Callable[..., Any],
        *args: Tuple[Any, ...],
        **kwargs: Dict[str, Any]
    ):
        return await asyncio.to_thread(
            call,
            *args,
            **kwargs
        )

    async def sequence(
        self,
        *jobs: Tuple[
            Coroutine[
                None,
                None,
                Any
            ]
        ]
    ):
        results: List[Any] = []

        for job in jobs:
            results.append(
                await job
            )

        return results

    async def batch(
        self,
        *jobs: Tuple[
            Coroutine[
                None,
                None,
                Any
            ]
        ],
        timeout: Optional[
            Union[int, float]
        ]=None
    ) -> List[Any]:

        completed_jobs: List[Any] = await asyncio.wait_for(
            asyncio.gather(*[
                job for job in jobs
            ]),
            timeout=timeout
        )

        results = []

        for completed_job in completed_jobs:

            if isinstance(completed_job, list):
                results.extend(completed_job)

            else:
                results.append(completed_job)
        
        return results

    async def finalize(
        self,
        timeout: float=None
    ) -> List[Any]:
        results = []
        for result in asyncio.as_completed(self.pending, timeout=timeout):
            results.append(await result)

        return results

    def defer(
        self,
        call: Callable[..., Coroutine[None, None, Any]],
        *args: Tuple[Any, ...],
        timeout: float=60,
        fail_on_timeout: bool = True,
        **kwargs: Dict[str, Any],

    ) -> None:
        self.pending.append(
            asyncio.create_task(
                self.wait(
                    call(*args, **kwargs),
                    timeout=timeout,
                    fail_on_timeout=fail_on_timeout
                )
            )
        )
    
    async def wait(
        self,
        call: Callable[..., Coroutine[None, None, Any]],
        timeout: float=60,
        fail_on_timeout: bool = True
    ) -> Union[Any, StepTimeoutError]:
        try:
            return await asyncio.wait_for(call, timeout=timeout)

        except (asyncio.TimeoutError, asyncio.CancelledError,):
            error = StepTimeoutError(
                call.__name__,
                self.__class__.__name__,
                timeout
            )

            if fail_on_timeout:
                raise error
            
            return error

    async def close(self):
        await self.system.close()
        await self.shell.close()

    def abort(self):
        self.system.abort()
        self.shell.abort()