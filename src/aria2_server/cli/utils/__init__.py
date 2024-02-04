import typer

# NOTE: had better NOT to import any `aria2_server` modules except `cli` modules
from aria2_server.cli.utils.mkcert import mkcert_cli

__all__ = ("utils_cli",)

utils_cli = typer.Typer(help="Utilities for aria2-server.", name="utils")


utils_cli.add_typer(mkcert_cli)

if __name__ == "__main__":
    utils_cli()
