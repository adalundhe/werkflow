import ntpath
import importlib
import sys
from typing import Dict, Union
from werkflow.cli.exceptions import (
    MultipleWorkflowsViolationError,
    EmptyWorkflowFileError
)
from werkflow.graph import Workflow, WorkflowGroup
from werkflow.modules.base import Module
from pathlib import Path

def import_workflow(path: str) -> Dict[str, Union[Workflow, Module]]:
    package_dir = Path(path).resolve().parent
    package_dir_path = str(package_dir)
    package_dir_module = package_dir_path.split('/')[-1]
    
    package = ntpath.basename(path)
    package_slug = package.split('.')[0]
    spec = importlib.util.spec_from_file_location(f'{package_dir_module}.{package_slug}', path)
    
    if path not in sys.path:
        sys.path.append(str(package_dir.parent))

    module = importlib.util.module_from_spec(spec)

    sys.modules[module.__name__] = module

    spec.loader.exec_module(module)

    workflows = list({cls.__name__: cls for cls in Workflow.__subclasses__()}.values())
    workflow_groups = list({cls.__name__: cls() for cls in WorkflowGroup.__subclasses__()}.values())
    modules = list({cls.__name__: cls for cls in Module.__subclasses__()}.values())

    prioritized_workflows = list(sorted(
        workflows,
        key=lambda workflow: workflow.priority
    ))

    default_workflow_group = WorkflowGroup()

    if len(workflow_groups) > 0:
        for group in workflow_groups:

            for workflow in prioritized_workflows:
                workflow_name = workflow.__name__

                if workflow_name not in group.workflow_names:
                    default_workflow_group.add_workflow(workflow)

        if len(default_workflow_group.group_workflows) > 0 :
            workflow_groups.append(default_workflow_group)

    else:
        for workflow in prioritized_workflows:
            workflow_name = workflow.__class__.__name__
            default_workflow_group.add_workflow(workflow)

        if len(default_workflow_group.group_workflows) > 0 :
            workflow_groups.append(default_workflow_group)

    groups_discovered = len(workflow_groups)

    if groups_discovered < 1:
        raise EmptyWorkflowFileError(path)
    
    elif groups_discovered > 1:
        raise MultipleWorkflowsViolationError(
            groups_discovered,
            path
        )
    
    else:
        workflow_group: WorkflowGroup = workflow_groups.pop()
        return {
            'workflow': workflow_group,
            'modules': [
                module() for module in modules
            ]
        }
