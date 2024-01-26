import click
import asyncio
import functools
from typing import List, Dict, Optional, Any, Callable, Union
from .option_prompt_validator import OptionPromptValidator
from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType


class OptionPrompt(BasePrompt):

    def __init__(
        self, 
        message: str, 
        skip: bool = False, 
        options: List[str] = None, 
        result_key: str = None, 
        default: Optional[Any] = None, 
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None, 
        confirmation_message: Optional[Union[str, Callable[..., str]]] = None, 
    ) -> None:
        super().__init__(
            message, 
            skip, 
            result_key, 
            default, 
            condition, 
            confirmation_message,
        )

        validated_prompt = OptionPromptValidator(
            prompt_data_type=click.Choice(
                options,
                case_sensitive=False
            ),
            prompt_type=PromptType.OPTION
        )

        self.options = validated_prompt.prompt_data_type
        self.prompt_type = validated_prompt.prompt_type
        

    async def ask(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                click.prompt,
                f'{self.prompt_frame} {self.message}',
                type=self.options,
                default=self.default,
                prompt_suffix='',
                show_choices=True
            )
        )