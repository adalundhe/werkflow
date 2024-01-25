import asyncio
import click
import os
import json
from werkflow.cli.signals import add_abort_handler
from werkflow.cli.import_tools.workflow import import_workflow
from werkflow.graph import (
    Graph,
    WorkflowGroup
)
from werkflow.logging import (
    WerkflowLogger,
    LoggerTypes,
    logging_manager
)
from werkflow.modules.base import Module
from typing import List


@click.group(help='Commands to run and manage workflows.')
def workflow():
    pass

@workflow.command(
    help='Run the workflow at the given path or by the given name.'
)
@click.option(
    '--ci',
    is_flag=True,
    help='Mute CLI graphics for CI compatability.'
)
@click.option(
    '--no-prompt',
    is_flag=True,
    help='Mute all interactive prompts and default to values in .werkflow.json.'
)
@click.option(
    '--config-path',
    show_default=True,
    default=f'{os.getcwd()}/.werkflow.json',
    help='Path to existing .werkflow.json.'
)
@click.option(
    '--log-level',
    default='info',
    help='Set log level.'
)
@click.option(
    '--logfiles-directory',
    show_default=True,
    default=f'{os.getcwd()}/logs',
    help='Output directory for logfiles. If the directory does not exist it will be created.'
)
@click.argument('path')
def run(
    ci: bool,
    no_prompt: bool,
    config_path: str,
    path: str,
    log_level: str,
    logfiles_directory: str
):
    werkflow_config = {}
    if os.path.exists(config_path):
        with open(config_path) as werkflow_config_file:
            werkflow_config = json.load(werkflow_config_file)

    werkflow_config['config_path'] = config_path

    disabled_loggers = [
        LoggerTypes.DISTRIBUTED,
        LoggerTypes.DISTRIBUTED_FILESYSTEM
    ]

    if ci:
        disabled_loggers.extend([
            LoggerTypes.SPINNER,
            LoggerTypes.WERKFLOW
        ])

    logging_manager.disable(*disabled_loggers)

    logging_manager.update_log_level(log_level)
    logging_manager.logfiles_directory = logfiles_directory

    if os.path.exists(logfiles_directory) is False:
        os.mkdir(logfiles_directory)

    elif os.path.isdir(logfiles_directory) is False:
        os.remove(logfiles_directory)
        os.mkdir(logfiles_directory)

    logger = WerkflowLogger()
    logger.initialize()

    discovered = import_workflow(path)
    workflow: WorkflowGroup = discovered.get('workflow')
    modules: List[Module] = discovered.get('modules')

    module_names = [module.__class__.__name__ for module in modules]
    
    logger['console'].sync.info(f'Loading graph - {workflow.__class__.__name__}')
    
    if len(modules) > 0:
        modules_loaded = ', '.join(module_names)
        logger['console'].sync.info(f'Using modules - {modules_loaded}')

    try:
        loop = asyncio.get_event_loop()

    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    logger.filesystem.sync.create_logfile('werkflow.core.log')
    logger.filesystem.create_filelogger('werkflow.core.log')

    graph = Graph(
        workflow,
        no_prompt=no_prompt,
        werkflow_config=werkflow_config
    )

    graph.setup()
    
    add_abort_handler(
        loop,
        logger,
        graph
    )

    loop.run_until_complete(graph.run())    

    if logger.spinner.logger_enabled:
        logger.console.sync.info(f'\nGraph - {workflow.__class__.__name__} - completed! {graph.logger.spinner.display.total_timer.elapsed_message}\n')

    else:
        logger.console.sync.info(f'\nGraph - {workflow.__class__.__name__} - completed!\n')