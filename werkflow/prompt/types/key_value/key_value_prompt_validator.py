from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType
from pydantic import BaseModel, StrictStr, StrictBool, validator
from typing import Callable, Optional, Any


class KeyValuePromptValidator(BaseModel):
    key_prompt: Any
    value_prompt: Any
    prompt_result_key: Optional[StrictStr]
    prompt_type: PromptType
    prompt_condition: Optional[Callable[..., StrictBool]]

    class Config:
        arbitrary_types_allowed=True

    @validator('key_prompt')
    def validate_key_prompt(cls, val):
        assert issubclass(type(val), BasePrompt)
        
        return val

    @validator('value_prompt')
    def validate_value_prompt(cls, val):
        assert issubclass(type(val), BasePrompt)

        return val

    @validator('prompt_type')
    def validate_type(cls, val):
        assert val == PromptType.KEY_VALUE

        return val
