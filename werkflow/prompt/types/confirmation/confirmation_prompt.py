import asyncio
import functools
import click
from typing import (
    Optional,
    Callable,
    Any,
    Dict,
    Union
)
from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType
from .confirmation_prompt_validator import ConfirmationPromptValidator


class ConfirmationPrompt(BasePrompt):

    def __init__(
        self, 
        message: str, 
        skip: bool = False, 
        result_key: str = None, 
        default: Optional[Any] = False, 
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None, 
        confirmation_message: Optional[Union[str, Callable[..., str]]] = None
    ) -> None:
        super().__init__(
            message, 
            skip, 
            result_key, 
            default, 
            condition, 
            confirmation_message
        )

        validator = ConfirmationPromptValidator(
            prompt_data_type=str,
            prompt_type=PromptType.CONFIRMATION
        )

        self.data_type = validator.prompt_data_type
        self.prompt_type = validator.prompt_type

    async def ask(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                click.confirm,
                f'{self.prompt_frame} {self.message}',
                default=self.default,
                abort=False,
                prompt_suffix=''
            )
        )