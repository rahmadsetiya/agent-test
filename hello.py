import argparse
import sys


def greet(name):
    return f"Hello, {name}!"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print a friendly greeting.")
    parser.add_argument("name", nargs="?", help="Name to greet")
    args = parser.parse_args(argv)
    if not args.name:
        print("Please provide a name.", file=sys.stderr)
        return 1
    print(greet(args.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
