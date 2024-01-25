import inspect
from collections import OrderedDict
from typing import List, Type, Dict
from .workflow import Workflow


class WorkflowGroup:
    workflows: List[Type[Workflow]]=[]

    def __init__(self) -> None:
        self.group_workflows: Dict[str, Workflow] = OrderedDict()
        self.workflow_names = []

        for workflow in self.workflows:
            new_workflow = type(workflow())()
            workflow_name = new_workflow.__class__.__name__

            new_workflow.__class__.__base__()
            
            self.group_workflows[workflow_name] = new_workflow
            self.workflow_names.append(workflow_name)

    def add_workflow(self, workflow: Type[Workflow]):
        new_workflow = workflow()

        new_workflow: Workflow = type(
                new_workflow.__class__.__name__, 
                (workflow, ), 
                dict(new_workflow.__dict__)
        )()
        
        new_workflow.__class__.__base__()

        workflow_name = new_workflow.__class__.__name__

        self.group_workflows[workflow_name] = new_workflow
        self.workflow_names.append(workflow_name)