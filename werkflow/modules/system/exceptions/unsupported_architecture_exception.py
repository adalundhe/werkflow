from typing import List


class UnsupportedArchitectureException(Exception):

    def __init__(
        self, 
        operating_system: str,
        provided_arch_option: str,
        supported_arch_options: List[str],
    ) -> None:

        supported_options = ', '.join(supported_arch_options)

        super().__init__(
            f'Unsupported architecture for {operating_system}.\n -Found: {provided_arch_option}\n- Supports: {supported_options}'
        )