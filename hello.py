import argparse


def greet(name):
    return f"Hello, {name}"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print a friendly greeting.")
    parser.add_argument("name", help="Name to greet")
    args = parser.parse_args(argv)
    print(greet(args.name))


if __name__ == "__main__":
    main()
