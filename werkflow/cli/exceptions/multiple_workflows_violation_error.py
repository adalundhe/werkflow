class MultipleWorkflowsViolationError(Exception):

    def __init__(
        self, 
        workflows_found: int,
        workflow_filepath: str
    ) -> None:
        super().__init__(
            f'Found {workflows_found} workflows in file or named workflow {workflow_filepath}.\nOnly one Workflow is allowed per file.'
        )