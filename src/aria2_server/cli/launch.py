import logging
from pathlib import Path
from typing import Optional

import tomli
import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from aria2_server import logger
from aria2_server.app import main as app_main
from aria2_server.config import get_current_config, reload
from aria2_server.config.schemas import Config
from aria2_server.logger import configure_default_logging

__all__ = ("launch_cli",)


launch_cli = typer.Typer(invoke_without_command=True)


def _load_config_from_file(file: str) -> "Config":
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
    else:
        config_model = None
    reload(config_model)

    global_config = get_current_config()

    uvicorn_logging_level = global_config.server.uvicorn_logging_level
    if uvicorn_logging_level == "trace":
        uvicorn_logging_level = "debug"

    logging_level = logging.getLevelName(uvicorn_logging_level.upper())
    assert isinstance(logging_level, int)

    configure_default_logging(logging_level)

    app_main()


if __name__ == "__main__":
    launch_cli()
