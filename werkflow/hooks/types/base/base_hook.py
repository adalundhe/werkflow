import uuid
import inspect
from typing import (
    Callable, 
    Any, 
    Tuple, 
    List,
    Dict
)
from werkflow.prompt.types.base.base_prompt import BasePrompt
from .hook_types import HookType


class BaseHook:

    def __init__(
        self,
        name: str,
        shortname: str,
        call: Callable[..., Any],
        *names: Tuple[str, ...],
        hook_type: HookType=None,
        prompts: List[BasePrompt]=[],
        skip_on_fail: bool=False,
        condition: Callable[
            [Dict[str, Any]],
            bool
        ]=None
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.shortname = shortname
        self._call = call
        self.names: List[str] = list(names)
        self.args = inspect.signature(call)
        self.params = self.args.parameters
        self.type = hook_type
        self.skip_on_fail = skip_on_fail
        self.namespace: str = None
        self.workflow: str = None
        self.prompts = prompts
        self.condition = condition

    async def call(self, **kwargs):

        hook_args = {
            name: value for name, value in kwargs.items() if name in self.params
        }
        
        if self.condition and self.condition(kwargs):
            result = await self._call(**hook_args)

        elif self.condition is None:
            result = await self._call(**hook_args)

        else:
            result = {}

        if isinstance(result, dict):
            return {
                **kwargs,
                **result
            }
        
        return {
            **kwargs,
            self.shortname: result
        }

