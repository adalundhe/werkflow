import asyncio
import click
import functools
from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType
from typing import Callable, Union, Optional, Any, Dict
from .repeat_prompt_validator import RepeatPromptValidator


class RepeatPrompt(BasePrompt):

    def __init__(
        self,
        prompt: BasePrompt,
        result_key: str=None,
        skip: bool=False,
        condition: Optional[Callable[[Dict[str, Any]], bool]]=None,
        break_condition: Callable[[Dict[str, Any]], bool]=lambda response: response is not None,
        confirmation_message: Optional[Union[str, Callable[..., str]]] = None, 

    ) -> None:
        super().__init__(
            None,
            skip,
            result_key,
            None,
            condition,
            confirmation_message
        )

        validated_prompt = RepeatPromptValidator(
            prompt_repeated=prompt,
            prompt_break_condition=break_condition,
            prompt_type=PromptType.REPEAT
        )

        self.prompt: BasePrompt = validated_prompt.prompt_repeated
        self.break_condition = validated_prompt.prompt_break_condition  
        self.prompt_type = validated_prompt.prompt_type

    async def ask(self):
        
        responses = []
        response = None

        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        while not self.break_condition(response):

            if response is not None:
                responses.append(response)

            response = await self.prompt.ask()
            await self.prompt.confirm(response)

            if not self.break_condition(response):
                await self._loop.run_in_executor(
                    self._executor,
                    functools.partial(
                        click.echo,
                        ''
                    )
                )

        return responses

    async def confirm(self, response: Any):
        if self.confirmation_message:

            if self._loop is None:
                self._loop = asyncio.get_running_loop()
            
            if isinstance(self.confirmation_message, str):
                confirmation_text = self.confirmation_message

            else:
                confirmation_text = self.confirmation_message(response)

            await self._loop.run_in_executor(
                self._executor,
                functools.partial(
                    click.echo,
                    f'{self.prompt.confirmation_frame} {confirmation_text}',
                )
            )

    def close(self):
        self.prompt.close()