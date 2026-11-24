class UnknownStepDependencyError(ValueError):

    def __init__(
        self,
        workflow_name: str,
        step_name: str,
        dependency_name: str,
        available_steps: list[str],
    ) -> None:
        available = ', '.join(sorted(available_steps)) or '(none)'
        super().__init__(
            f"Step '{step_name}' in workflow '{workflow_name}' depends on unknown step "
            f"'{dependency_name}'. Available steps: {available}"
        )
