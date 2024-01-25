from werkflow.modules.base import Module
from pydantic import BaseModel, validator
from typing import Tuple, Type


class RequiresValidator(BaseModel):
    modules: Tuple[Type[Module], ...]

    class Config:
        allow_arbitrary_types=True

    @validator('modules')
    def validate(cls, val: Tuple[Type[Module], ...]):
        assert len(val) > 0
        
        for module_type in val:
            assert issubclass(module_type, Module), "Only Modules can be provided to the @requires hook."

            module_dependencies = f'\n\t-'.join(module_type.dependencies)

            assert module_type.module_enabled is True, f"The {module_type.__name__} Module is missing or its dependencies:\n\n\t-{module_dependencies}\n\n  have not been installed."

        return val