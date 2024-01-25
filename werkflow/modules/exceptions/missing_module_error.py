from werkflow.modules.base import Module


class MissingModuleError(Exception):

    def __init__(
        self,
        module: Module
    ): 
        module_name = module.__class__.__name__
        dependencies = module.dependencies

        dependency_names = '\n\t-'.join(dependencies)

        super().__init__(
            f'Module {module_name} is missing or its dependencies:\n\t-{dependency_names}\nhave not been installed.'
        )