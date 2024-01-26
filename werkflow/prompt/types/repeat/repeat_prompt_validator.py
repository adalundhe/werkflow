from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType
from pydantic import BaseModel, StrictBool, validator
from typing import Callable, Any, Union


class RepeatPromptValidator(BaseModel):
    prompt_repeated: object
    prompt_break_condition: Callable[..., StrictBool]
    prompt_type: PromptType

    class Config:
        arbitrary_types_allowed=True

    @validator('prompt_repeated')
    def validate_prompt(cls, val):
        assert issubclass(type(val), BasePrompt)

        return val

    @validator('prompt_type')
    def validate_type(cls, val):
        assert val == PromptType.REPEAT

        return val
