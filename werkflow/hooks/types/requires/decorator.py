from werkflow.modules.base import Module
from typing import Tuple, Type
from .validator import RequiresValidator


def requires(*modules: Tuple[Type[Module], ...]):

    RequiresValidator(
        modules=modules
    )

    def wraps(cls: Type[Module]):

        return cls
    
    return wraps