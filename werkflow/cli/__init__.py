import click
from .base import CLI

@click.group(cls=CLI)
def run():
    pass
