from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
)

from pydantic import BaseModel, StrictBool, StrictStr

from werkflow.prompt.types.base.base_prompt import BasePrompt


class StepHookCheckpoint(BaseModel):
    serializer: Literal['json', 'bytes'] = 'json'
    action: Literal['load', 'save']
    path: StrictStr

class StepHookValidator(BaseModel):
    names: Tuple[StrictStr, ...]
    prompts: List[BasePrompt]=[]
    skip_on_fail: StrictBool
    condition: Optional[
        Callable[
            [Dict[str, Any]],
            bool
        ]
    ]=None
    checkpoint: StepHookCheckpoint | None = None

    class Config:
        arbitrary_types_allowed=True

