import click
import asyncio
import functools
from typing import Dict, Type, Optional, Any, Callable, Union
from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType
from .secure_prompt_validator import SecurePromptValidator


class SecurePrompt(BasePrompt):

    def __init__(
        self, 
        message: str, 
        skip: bool = False, 
        result_key: str = None, 
        data_type: Type = str,
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

        validated_prompt = SecurePromptValidator(
            prompt_data_type=data_type,
            prompt_type=PromptType.SECURE
        )

        self.data_type = validated_prompt.prompt_data_type
        self.prompt_type = validated_prompt.prompt_type
        

    async def ask(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        return await self._loop.run_in_executor(
            self._executor,
            functools.partial(
                click.prompt,
                f'{self.prompt_frame} {self.message}',
                type=self.data_type,
                default=self.default,
                hide_input=True,
                prompt_suffix=''
            )
        )