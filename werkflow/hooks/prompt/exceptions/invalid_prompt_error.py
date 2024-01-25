from typing import List


class InvalidPromptError(Exception):

    def __init__(
        self, 
        invalid_prompt_name: str, 
        existing_prompt_names: List[str]
    ) -> None:
        
        valid_prompt_names = '\n\t-'.join(existing_prompt_names)

        super().__init__(
            f'Interactive Prompt {invalid_prompt_name} not registered.\nRegistered prompts include:\n\t-{valid_prompt_names}'
        )