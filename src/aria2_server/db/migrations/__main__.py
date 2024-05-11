import argparse
from typing import Optional, Sequence

from alembic import command

from aria2_server import logger
from aria2_server.db.migrations import get_current_cfg

__all__ = ("argparser", "main")

# TODO: add docs/help
argparser = argparse.ArgumentParser()
sub_argparser = argparser.add_subparsers(required=True, dest="command")

upgrade_parser = sub_argparser.add_parser("upgrade")
upgrade_parser.add_argument("--revision", default="head")

revision_parser = sub_argparser.add_parser("revision")
revision_parser.add_argument("--message", "-m")


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = argparser.parse_args(argv)

    logger.debug(f"args: {args}")
    current_cfg = get_current_cfg()

    if args.command == "upgrade":
        command.upgrade(current_cfg, revision=args.revision)
    elif args.command == "revision":
        command.revision(current_cfg, message=args.message, autogenerate=True)


if __name__ == "__main__":
    main()
