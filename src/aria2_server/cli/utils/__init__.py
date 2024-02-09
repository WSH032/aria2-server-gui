"""Utilities for aria2-server.

NOTE: This package must isolate from other modules/packages of `aria2_server`,
    especially, this package should never import `config.GLOBAL_CONFIG`,
    or any var in other modules which is initialized by `config.GLOBAL_CONFIG`,
    because the `GLOBAL_CONFIG` has not been initialized yet.
"""

import typer

# NOTE: DO NOT to import any `aria2_server` modules except `cli` modules
from aria2_server.cli.utils.mkcert import mkcert_cli

__all__ = ("utils_cli",)

utils_cli = typer.Typer(help="Utilities for aria2-server.", name="utils")


utils_cli.add_typer(mkcert_cli)

if __name__ == "__main__":
    utils_cli()
