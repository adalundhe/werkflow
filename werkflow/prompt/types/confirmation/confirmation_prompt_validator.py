from pydantic import (
    BaseModel,
    validator
)
from werkflow.prompt.types.base.prompt_type import PromptType
from typing import Type


class ConfirmationPromptValidator(BaseModel):
    prompt_data_type: Type[str]
    prompt_type: PromptType

    class Config:
        arbitrary_types_allowed=True

    @validator('prompt_type')
    def validate_type(cls, val):
        assert val == PromptType.CONFIRMATION

        return val

