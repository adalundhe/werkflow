import click
from pydantic import (
    BaseModel,
    StrictBool,
    StrictStr,
    StrictInt,
    validator
)
from typing import Type, TypeVar
from werkflow.prompt.types.base.prompt_type import PromptType

T = TypeVar('T')


class InputPromptValidator(BaseModel):
    prompt_data_type: Type[T]
    prompt_type: PromptType

    class Config:
        arbitrary_types_allowed=True

    @validator('prompt_type')
    def validate_type(cls, val):
        assert val == PromptType.INPUT
        
        return val

