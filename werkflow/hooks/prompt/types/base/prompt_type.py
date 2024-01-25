from enum import Enum


class PromptType(Enum):
    INPUT='INPUT'
    CONFIRMATION='CONFIRMATION'
    OPTION='OPTION'
    SECURE='SECURE'
    KEY_VALUE='KEY_VALUE'
    REPEAT='REPEAT'