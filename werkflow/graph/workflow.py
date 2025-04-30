import asyncio
from collections import deque
from typing import Any, Callable, Coroutine, Deque, Dict, List, Optional, Tuple, Union

from werkflow.logging import WerkflowLogger

from .exceptions import StepTimeoutError


class Workflow:
    priority=1

    def __init__(self) -> None: 

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
            asyncio.gather(*jobs),
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
        pass

    def abort(self):
        pass