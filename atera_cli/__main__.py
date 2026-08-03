"""Entry point for running the toolkit as `python -m atera_cli`."""

import sys

from atera_cli.cli import main

if __name__ == "__main__":
    sys.exit(main())
