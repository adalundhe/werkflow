class StepTimeoutError(Exception):

    def __init__(
        self, 
        step_name: str, 
        workflow_name: str,
        timeout: float
    ) -> None:
        super().__init__(
            f'Step - {step_name} - for workflow - {workflow_name} - timed out after - {timeout} - seconds.'
        )