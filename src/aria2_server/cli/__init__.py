import typer

from aria2_server.cli.launch import launch_cli
from aria2_server.cli.utils import utils_cli

__all__ = ("cli",)


cli = typer.Typer(help="aria2-server command line interface.")


cli.add_typer(launch_cli)
cli.add_typer(utils_cli)

if __name__ == "__main__":
    cli()
