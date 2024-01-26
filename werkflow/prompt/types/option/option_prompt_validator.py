import click
from pydantic import (
    BaseModel,
    validator
)
from werkflow.prompt.types.base.prompt_type import PromptType


class OptionPromptValidator(BaseModel):
    prompt_data_type: click.Choice
    prompt_type: PromptType

    class Config:
        arbitrary_types_allowed=True

    @validator('prompt_type')
    def validate_type(cls, val):
        assert val == PromptType.OPTION

        return val

