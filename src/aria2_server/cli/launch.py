from pathlib import Path
from typing import TYPE_CHECKING, Optional

import tomli
import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from aria2_server import logger

# NOTE: had better NOT to import any `aria2_server` modules before calling `reload()` in `main()`

if TYPE_CHECKING:
    from aria2_server.config.schemas import Config


__all__ = ("launch_cli",)


launch_cli = typer.Typer(invoke_without_command=True)


def _load_config_from_file(file: str) -> "Config":
    from aria2_server.config.schemas import Config

    try:
        with typer.open_file(file, mode="rb") as f:
            # HACK, FIXME: This is type hint issue,
            # see https://github.com/microsoft/pyright/issues/831
            toml_dict = tomli.load(f)  # pyright: ignore[reportArgumentType]
    except tomli.TOMLDecodeError as e:
        logger.critical(f"{file} is not a valid TOML file\n{e}")
        raise

    try:
        return Config.model_validate(toml_dict)
    except ValidationError as e:
        logger.critical(f"{file} is not a valid config file\n{e}")
        raise


@launch_cli.callback()
def launch(
    config: Annotated[
        Optional[Path],
        typer.Option(
            help="aria2-server config file path",
            dir_okay=False,
            readable=True,
            allow_dash=True,
        ),
    ] = None,
) -> None:
    """Launch aria2-server."""
    if config is not None:
        logger.info(f"Loading config from: {config}")
        config_model = _load_config_from_file(str(config))
        logger.info(f"Loaded config:\n{config_model.model_dump_json(indent=4)}")
        from aria2_server.config import reload

        reload(config_model)

    from aria2_server.app.main import main as app_main

    app_main()


if __name__ == "__main__":
    launch_cli()
