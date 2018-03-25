"""
Example test code
"""
from argparse import ArgumentParser, FileType
from json import loads

from .server import serve
from .planner import initialize

def main():
    cli = ArgumentParser()
    cli.add_argument("--port", type=int, default=8000, help="http port number")
    cli.add_argument("--ignore-items", type=str, default="")
    cli.add_argument("dump", type=FileType("r"), help="")
    args = cli.parse_args()

    ignored_items = set()
    for item in args.ignore_items.split(","):
        item = item.strip()
        if item:
            ignored_items.add(item)

    initialize(loads(args.dump.read()), ignored_items)

    print("listening on port %d" % args.port)
    serve(args.port)

if __name__ == '__main__':
    main()
