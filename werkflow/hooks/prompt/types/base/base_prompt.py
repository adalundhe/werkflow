import asyncio
import functools
import click
from concurrent.futures import ThreadPoolExecutor
from werkflow.modules.system import System
from termcolor import colored
from typing import Optional, Any, Callable, Union, Dict
from .base_prompt_validator import BasePromptValidator


class BasePrompt:

    def __init__(
        self,
        message: str,
        skip: bool=False,
        result_key: str=None,
        default: Optional[Any]=None,
        condition: Optional[Callable[..., bool]] = None, 
        confirmation_message: Optional[Union[str, Callable[..., str]]] = None, 
    ) -> None:

        system = System()

        self._loop: asyncio.AbstractEventLoop = None
        self._executor = ThreadPoolExecutor(
            max_workers=system.configuration.cores.physical
        )

        self.prompt_color = 'cyan'
        self.prompt_frame = colored('●', color=self.prompt_color)
        self.confirmation_frame = colored('✔', color=self.prompt_color)

        validated_prompt = BasePromptValidator(
            prompt_message=message,
            prompt_skipped=skip,
            prompt_result_key=result_key,
            prompt_default=default,
            prompt_condition=condition,
            prompt_confirmation_message=confirmation_message
        )

        self.message = validated_prompt.prompt_message
        self.skipped = validated_prompt.prompt_skipped
        self.result_key = validated_prompt.prompt_result_key
        self.default = validated_prompt.prompt_default
        self.condtition = validated_prompt.prompt_condition
        self.confirmation_message = validated_prompt.prompt_confirmation_message

    async def ask(self):
        raise NotImplementedError('Ask method not implemented on base Prompt class.')

    async def confirm(self, response: Any):
        if self.confirmation_message:
            
            if isinstance(self.confirmation_message, str):
                confirmation_text = self.confirmation_message

            else:
                confirmation_text = self.confirmation_message(response)

            await self._loop.run_in_executor(
                self._executor,
                functools.partial(
                    click.echo,
                    f'{self.confirmation_frame} {confirmation_text}',
                )
            )

    def close(self):
        self._executor.shutdown()