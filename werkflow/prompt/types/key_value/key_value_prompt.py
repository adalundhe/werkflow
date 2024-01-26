import click
import functools
from werkflow.prompt.types.base.base_prompt import BasePrompt
from werkflow.prompt.types.base.prompt_type import PromptType
from typing import Callable, Union, Optional, Any, Dict
from .key_value_prompt_validator import KeyValuePromptValidator


class KeyValuePrompt(BasePrompt):

    def __init__(
        self,
        key_prompt: BasePrompt=None,
        value_prompt: BasePrompt=None,
        result_key: str=None,
        skip: bool=False,
        condition: Optional[Callable[[Dict[str, Any]], bool]]=None

    ) -> None:
        
        super().__init__(
            None,
            skip,
            result_key,
            None,
            condition,
            None
        )

        validated_prompt = KeyValuePromptValidator(
            key_prompt=key_prompt,
            value_prompt=value_prompt,
            prompt_result_key=result_key,
            prompt_type=PromptType.KEY_VALUE,
            prompt_condition=condition
        )

        self.key_prompt: BasePrompt = validated_prompt.key_prompt
        self.value_prompt: BasePrompt = validated_prompt.value_prompt
        self.prompt_type = validated_prompt.prompt_type

    async def ask(self):    
        key_response = await self.key_prompt.ask()

        if key_response == self.key_prompt.default:
            return {
                'key': key_response,
                'value': None
            }

        await self.key_prompt.confirm(key_response)

        value_response = await self.value_prompt.ask()
        await self.value_prompt.confirm(value_response)

        return {
            'key': key_response,
            'value': value_response
        }

    async def confirm(self, _: Any):
        pass

    def close(self):
        self.key_prompt.close()
        self.value_prompt.close()