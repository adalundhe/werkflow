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
        prompts: List[BasePrompt] | None = None,
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
        self.prompts = list(prompts) if prompts is not None else []
        self.condition = condition

    async def call(
        self, 
        return_on_failure: bool = True,
        **kwargs
    ):

        hook_args = {
            name: value for name, value in kwargs.items() if name in self.params
        }

        if self.condition is not None and not self.condition(kwargs):
            return {}

        try:
            result: Any | Exception = await self._call(**hook_args)

        except Exception as execution_error:
            if return_on_failure or self.skip_on_fail:
                return execution_error
            raise execution_error
        
        if isinstance(result, Exception):
            if return_on_failure or self.skip_on_fail:
                return result
            raise result

        if result is None:
            return {}

        if isinstance(result, dict):
            return dict(result)
        
        return {
            self.shortname: result
        }

