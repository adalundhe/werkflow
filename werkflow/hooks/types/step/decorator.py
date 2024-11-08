import functools
from typing import Any, Callable, Dict, List, Literal

from werkflow.hooks.types.base.hook_types import HookType
from werkflow.hooks.types.base.registrar import registrar
from werkflow.prompt.types.base.base_prompt import BasePrompt

from .validator import StepHookCheckpoint, StepHookValidator


@registrar(HookType.STEP)
def step(
    *names, 
    prompts: List[BasePrompt]=[], 
    skip_on_fail: bool=False,
    condition: Callable[[
        Dict[str, Any]
    ], bool]=None,
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
):
    
    validated_checkpoint: StepHookCheckpoint | None = None
    if validated_checkpoint:
        validated_checkpoint = StepHookCheckpoint(**checkpoint)

    StepHookValidator(
        names=names,
        prompts=prompts,
        skip_on_fail=skip_on_fail,
        condition=condition,
        checkpoint=validated_checkpoint,
    )

    def wrapper(func):

        @functools.wraps(func)
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)
        
        return decorator
    return wrapper