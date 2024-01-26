"""NOTE: This is a private module only for launching from the command line."""

import argparse
import logging
import sys
from pathlib import Path

import tomli
from pydantic import ValidationError

from aria2_server.app.main import main as app_main
from aria2_server.config import reload
from aria2_server.config.schemas import Config

__all__ = ("main",)


def _load_config_from_file(file: Path) -> Config:
    try:
        with file.open("rb") as f:
            toml_dict = tomli.load(f)
    except tomli.TOMLDecodeError as e:
        logging.critical(f"Config file {file} is not a valid TOML file\n{e}")
        raise

    try:
        return Config.model_validate(toml_dict)
    except ValidationError as e:
        logging.critical(f"Config file {file} is not a valid config file\n{e}")
        raise


_cmd_parser = argparse.ArgumentParser()
_cmd_parser.add_argument(
    "--config",
    "-c",
    type=Path,
    default=None,
    help="aria2-server config file path",
)


def main():
    cmd_opts = _cmd_parser.parse_args()
    conf_file_path = cmd_opts.config

    if conf_file_path is not None:
        assert isinstance(conf_file_path, Path)
        logging.info(f"Loading config from: {conf_file_path}")
        if not conf_file_path.is_file():
            sys.exit(
                f"Config file '{conf_file_path}', which is set via cli, does not exist"
            )
        config = _load_config_from_file(conf_file_path)
        logging.info(f"Loaded config:\n{config.model_dump_json(indent=4)}")
        reload(config)

    app_main()


if __name__ == "__main__":
    main()
