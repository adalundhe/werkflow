import click


@click.group(help="Commands to setup global developer environment or a project.")
def setup():
    pass


@setup.command(help='Install custom dependencies or environment')
@click.argument('name')
@click.option(
    '--type',
    default='python',
    help='Resource type to use for installation.'
)
@click.option(
    '--env-version',
    default='latest',
    help='Version of language/resource to use.'
)
@click.option(
    '--using',
    default='',
    help='Comma-delimited list of dependencies/requirements.'
)
def install(
    name: str,
    type: str,
    env_version: str,
    using: str
):
    dependencies = using.split(',')