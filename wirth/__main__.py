import argparse
import sys

from .validate import validate


def main():
    parser = argparse.ArgumentParser(description="Validate contract structure and file references only.")
    parser.add_argument("command", choices=["validate"])
    parser.parse_args()
    errors = validate()
    if errors:
        print(*errors, sep="\n", file=sys.stderr)
        return 1
    print("contract structure valid; checks were not run and evidence adequacy was not assessed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
