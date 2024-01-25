class EmptyWorkflowFileError(Exception):

    def __init__(self, path: str) -> None:
        super().__init__(
            f'Specified file or named workflow at {path} is empty.\n Please add a workflow.'
        )