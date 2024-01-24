import argparse
from typing import Optional, Sequence

from aria2_server.db.migrations import revision, upgrade

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

    print(f"args: {args}")

    if args.command == "upgrade":
        upgrade(revision=args.revision)
    elif args.command == "revision":
        revision(message=args.message)


if __name__ == "__main__":
    main()
