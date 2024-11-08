from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Tuple,
)

from werkflow.hooks.types.base.base_hook import BaseHook
from werkflow.hooks.types.base.hook_types import HookType
from werkflow.prompt.types.base.base_prompt import BasePrompt


class StepHook(BaseHook):

    def __init__(
            self, name: str, 
            shortname: str, 
            call: Callable[..., Any], 
            *names: Tuple[str, ...],
            prompts: List[BasePrompt]=[],
            skip_on_fail: bool=False,
            condition: Callable[
                [Dict[str, Any]],
                bool
            ]=None,
            checkpoint: Dict[
                Literal[
                    'serializer', 
                    'path', 
                    'action',
                ], 
                str | Literal[
                    'load', 
                    'save',
                ],
            ] | None = None,
        ) -> None:

        super().__init__(
            name, 
            shortname,
            call, 
            *names,
            hook_type=HookType.STEP,
            prompts=prompts,
            skip_on_fail=skip_on_fail,
            condition=condition,
        )

        self.checkpoint = checkpoint
