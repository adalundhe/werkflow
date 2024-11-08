import inspect
import uuid
from typing import Any, Callable, Dict, List, Tuple

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

    async def call(
        self, 
        return_on_failure: bool = True,
        **kwargs
    ):

        hook_args = {
            name: value for name, value in kwargs.items() if name in self.params
        }

        result = {}
        
        try:
            if self.condition and self.condition(kwargs):
                result: Any | Exception = await self._call(**hook_args)

            elif self.condition is None:
                result: Any | Exception = await self._call(**hook_args)

        except Exception as execution_error:
            
            if return_on_failure:
                return execution_error
            
            raise execution_error
        
        if isinstance(result, Exception):
            return result

        elif isinstance(result, dict):
            return {
                **kwargs,
                **result
            }
        
        return {
            **kwargs,
            self.shortname: result
        }

