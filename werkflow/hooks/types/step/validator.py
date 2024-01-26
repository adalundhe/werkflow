from pydantic import BaseModel, StrictStr, StrictBool
from werkflow.prompt.types.base.base_prompt import BasePrompt
from typing import Tuple, List, Optional, Callable, Dict, Any


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

    class Config:
        arbitrary_types_allowed=True

