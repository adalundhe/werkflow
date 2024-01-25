import asyncio
import networkx
import inspect
import functools
import click
import os
from typing import Dict, List, Any
from dotenv import dotenv_values
from werkflow.hooks.types.base.base_hook import BaseHook
from werkflow.hooks.types.base.registrar import registrar
from werkflow.logging import WerkflowLogger
from .workflow_group import WorkflowGroup
from .workflow import Workflow


class Graph:

    def __init__(
        self,
        workflows: WorkflowGroup,
        no_prompt: bool=False,
        werkflow_config: Dict[str, Any]={}
    ) -> None:

        self.logger = WerkflowLogger()
        self.logger.initialize()

        self._no_prompt = no_prompt
        self._werkflow_config = werkflow_config
        self._project_options: Dict[str, Any] = self._werkflow_config.get(
            'project_options', {}
        )

        self._env = {}
        
        dot_env_path = f'{os.getcwd()}/.env'
        if os.path.exists(dot_env_path):
            self._env = dotenv_values(dot_env_path)

        self._project_options.update({
            key.lower(): value for key, value in self._env.items()
        })

        self._project_options['command_directory'] = os.getcwd()

        self._graphs: Dict[str, networkx.DiGraph] = {}
        self._execution_orders: Dict[str, List[List[str]]] = {}
        self._workflows: Dict[str, Workflow] = workflows.group_workflows
        self._workflow_hooks: Dict[str, Dict[str, BaseHook]] = {}

    def setup(self):

        for workflow in self._workflows.values():

            workflow.werkflow_config.update(self._werkflow_config)

            workflow_graph = networkx.DiGraph()
            workflow_hooks = {}
            workflow_name = workflow.__class__.__name__

            workflow_methods = inspect.getmembers(
                workflow, 
                predicate=inspect.ismethod
            )

            for _, method in workflow_methods:
                hook = registrar.all.get(method.__qualname__)

                if hook:
                    hook.workflow = workflow_name

                    hook._call = hook._call.__get__(workflow, workflow.__class__)
                    setattr(workflow, hook.shortname, hook._call)

                    workflow_hooks[hook.shortname] = hook

            workflow_graph.add_nodes_from([
                (
                    hook_name, 
                    {"hook": hook}
                ) for hook_name, hook in workflow_hooks.items()
            ])
            
            for hook in workflow_hooks.values():
                for dependency in hook.names:
                    if workflow_graph.nodes.get(dependency):
                        workflow_graph.add_edge(dependency, hook.shortname)

            execution_order: List[List[str]] = [
                generation for generation in networkx.topological_generations(workflow_graph)
            ]

            self._execution_orders[workflow_name] = execution_order
            self._workflow_hooks[workflow_name] = workflow_hooks
            self._graphs[workflow_name] = workflow_graph

    async def run(self):

        next_args: Dict[str, Any] = dict(self._project_options)

        loop = asyncio.get_running_loop()

        for workflow_name, execution_order in self._execution_orders.items():
            
            workflow = self._workflows.get(workflow_name)
            workflow_hooks = self._workflow_hooks.get(workflow_name)


            for generation in execution_order:
                generation_hooks: List[BaseHook] = [
                    workflow_hooks.get(hook_name) for hook_name in generation
                ]

                current_steps = ', '.join(
                    list(set([step.shortname for step in generation_hooks]))
                )

                if self.logger.spinner.logger_enabled:
                    await self.logger.spinner.append_message(f"Executing steps - {current_steps}")

                generation_prompts = []
                hooks_with_prompts = []
                for hook in generation_hooks:
                    hook_prompts = [hook for hook in generation_hooks if len(hook.prompts) > 0]
                    generation_prompts.extend(hook_prompts)

                    if len(hook_prompts) > 0:
                        hooks_with_prompts.append(hook.name)

                for hook in generation_hooks:
                    for prompt in hook.prompts:

                        result_key = prompt.result_key
                        if result_key is None:
                            result_key = hook.shortname

                        result_env_key = result_key.upper()
                        if self._no_prompt:
                            result = self._project_options.get(prompt.result_key)

                            if result is None:
                                result = await loop.run_in_executor(
                                    None,
                                    functools.partial(
                                        os.getenv,
                                        result_env_key
                                    )
                                )

                            if result is not None:
                                next_args[result_key] = result
                            
                        skipped = prompt.skipped
                        if prompt.condtition:
                            skipped = prompt.condtition(next_args) is False

                        if skipped is False and self._no_prompt is False:

                            await loop.run_in_executor(
                                None,
                                functools.partial(
                                    click.echo,
                                    ''
                                )
                            )

                            result = await prompt.ask()
                            await prompt.confirm(result)
                            next_args[result_key] = result

                            prompt.close()

                if self.logger.spinner.logger_enabled:
                    async with self.logger.spinner as status_spinner:
                        results: List[Dict[str, Any]] = await asyncio.gather(*[
                            asyncio.create_task(hook.call(
                                **next_args
                            )) for hook in generation_hooks
                        ])

                        status_spinner.group_finalize()
                        await status_spinner.ok('✔')

                else:
                    results: List[Dict[str, Any]] = await asyncio.gather(*[
                        asyncio.create_task(hook.call(
                            **next_args
                        )) for hook in generation_hooks
                    ])

                for result in results:
                    next_args.update({
                        result_key: result_value for result_key, result_value in result.items() if result_value is not None
                    })

            await workflow.close()

       
