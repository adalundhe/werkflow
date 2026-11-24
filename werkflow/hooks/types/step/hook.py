import asyncio
import json
import os
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Tuple,
)

from werkflow.hooks.types.base.base_hook import BaseHook
from werkflow.hooks.types.base.hook_types import HookType
from werkflow.prompt.types.base.base_prompt import BasePrompt

from .validator import StepHookCheckpoint, StepHookValidator


class StepHook(BaseHook):

    def __init__(
            self, name: str, 
            shortname: str, 
            call: Callable[..., Any], 
            *names: Tuple[str, ...],
            prompts: List[BasePrompt] | None = None,
            skip_on_fail: bool=False,
            condition: Callable[
                [Dict[str, Any]],
                bool
            ]=None,
            checkpoint: StepHookCheckpoint | Dict[
                Literal[
                    'serializer', 
                    'path', 
                    'action',
                ], 
                str | Literal[
                    'load', 
                    'save',
                ],
            ] | None = None,
        ) -> None:

        validated_checkpoint: StepHookCheckpoint | None = None
        if isinstance(checkpoint, StepHookCheckpoint):
            validated_checkpoint = checkpoint
        elif checkpoint is not None:
            validated_checkpoint = StepHookCheckpoint(**checkpoint)

        StepHookValidator(
            names=tuple(names),  # type: ignore[arg-type]
            prompts=list(prompts) if prompts is not None else [],
            skip_on_fail=skip_on_fail,
            condition=condition,
            checkpoint=validated_checkpoint,
        )

        super().__init__(
            name, 
            shortname,
            call, 
            *names,
            hook_type=HookType.STEP,
            prompts=prompts,
            skip_on_fail=skip_on_fail,
            condition=condition,
        )

        self.checkpoint: StepHookCheckpoint | None = validated_checkpoint

    def _load_checkpoint_sync(self, checkpoint: StepHookCheckpoint) -> Dict[str, Any]:
        if checkpoint.serializer == 'bytes':
            with open(checkpoint.path, 'rb') as checkpoint_file:
                return {self.shortname: checkpoint_file.read()}

        with open(checkpoint.path, 'r', encoding='utf-8') as checkpoint_file:
            loaded = json.load(checkpoint_file)

        if isinstance(loaded, dict):
            return loaded
        return {self.shortname: loaded}

    def _save_checkpoint_sync(
        self,
        checkpoint: StepHookCheckpoint,
        output: Dict[str, Any],
    ) -> None:
        parent = os.path.dirname(os.path.abspath(checkpoint.path))
        if parent:
            os.makedirs(parent, exist_ok=True)

        if checkpoint.serializer == 'bytes':
            if (
                len(output) == 1
                and self.shortname in output
                and isinstance(output[self.shortname], (bytes, bytearray))
            ):
                raw_bytes = bytes(output[self.shortname])
            else:
                raw_bytes = json.dumps(output, default=str).encode('utf-8')
            with open(checkpoint.path, 'wb') as checkpoint_file:
                checkpoint_file.write(raw_bytes)
            return

        with open(checkpoint.path, 'w', encoding='utf-8') as checkpoint_file:
            json.dump(output, checkpoint_file, default=str)

    async def call(
        self,
        return_on_failure: bool = True,
        **kwargs,
    ):
        if (
            self.checkpoint is not None
            and self.checkpoint.action == 'load'
            and await asyncio.to_thread(os.path.exists, self.checkpoint.path)
        ):
            try:
                return await asyncio.to_thread(
                    self._load_checkpoint_sync,
                    self.checkpoint,
                )
            except Exception as load_error:
                if return_on_failure or self.skip_on_fail:
                    return load_error
                raise load_error

        output = await super().call(
            return_on_failure=return_on_failure,
            **kwargs,
        )

        if (
            not isinstance(output, Exception)
            and self.checkpoint is not None
            and self.checkpoint.action == 'save'
        ):
            try:
                await asyncio.to_thread(
                    self._save_checkpoint_sync,
                    self.checkpoint,
                    output,
                )
            except Exception as save_error:
                if return_on_failure or self.skip_on_fail:
                    return save_error
                raise save_error

        return output
