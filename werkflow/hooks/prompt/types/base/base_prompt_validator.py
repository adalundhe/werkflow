from pydantic import (
    BaseModel,
    StrictBool,
    StrictStr
)
from typing import (
    Union, 
    Optional,
    Callable,
)


class BasePromptValidator(BaseModel):
    prompt_message: Optional[StrictStr]
    prompt_skipped: StrictBool
    prompt_result_key: Optional[str]
    prompt_default: Optional[Union[int, float, str, bool]]
    prompt_condition: Optional[Callable[..., bool]]
    prompt_confirmation_message: Optional[Union[Callable[..., StrictStr], StrictStr]]

