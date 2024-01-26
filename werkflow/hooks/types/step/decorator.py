import functools
from typing import List, Callable, Dict, Any
from werkflow.hooks.types.base.registrar import registrar
from werkflow.hooks.types.base.hook_types import HookType
from werkflow.prompt.types.base.base_prompt import BasePrompt
from .validator import StepHookValidator

@registrar(HookType.STEP)
def step(
    *names, 
    prompts: List[BasePrompt]=[], 
    skip_on_fail: bool=False,
    condition: Callable[[
        Dict[str, Any]
    ], bool]=None
):

    StepHookValidator(
        names=names,
        prompts=prompts,
        skip_on_fail=skip_on_fail,
        condition=condition
    )

    def wrapper(func):

        @functools.wraps(func)
        def decorator(*args, **kwargs):
            func(*args, **kwargs)
        
        return decorator
    return wrapper