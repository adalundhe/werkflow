import platform
from typing import List


class UnsupportedOperatingSystemException(Exception):

    def __init__(
        self, 
        supported_os_options: List[str]
    ) -> None:

        supported_options = ', '.join(supported_os_options)
        detected_os = platform.system()

        super().__init__(
            f'Unsupported OS.\n -Found: {detected_os}\n- Supports: {supported_options}'
        )