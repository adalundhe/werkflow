from typing import Dict, Type
from werkflow.hooks.types.step.hook import StepHook
from .base_hook import BaseHook
from .hook_types import HookType


class Registrar:
    all: Dict[str, BaseHook]={}
    module_paths: Dict[str, str] = {}

    def __init__(self, hook_type: HookType) -> None:
        self._hook_type = hook_type
        self._hook_types_map = {
            HookType.STEP: lambda *args, **kwargs: StepHook(
                *args,
                **kwargs
            )
        }

    def __call__(self, hook):
        hook = self._hook_types_map.get(self._hook_type)
        self.module_paths[hook.__name__] = hook.__module__

        def wrap_hook(*args, **kwargs):

            def wrapped_method(func):

                hook_name = func.__qualname__
                hook_shortname = func.__name__

                hook = self._hook_types_map[self._hook_type]

                hook_args = args
                args_count = len(args)
                
                if args_count < 1:
                    hook_args = []

                self.all[hook_name] = hook(
                    hook_name,
                    hook_shortname,
                    func,
                    *hook_args,
                    **kwargs
                )
                
                return func
            
            return wrapped_method

        return wrap_hook



def makeRegistrar() -> Type[Registrar]:
    return Registrar

registrar = makeRegistrar()