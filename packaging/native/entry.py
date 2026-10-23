"""The program PyInstaller builds: the same `squidbrake` command pip installs."""
import sys

from squidbrake.cli import main

if __name__ == "__main__":
    sys.exit(main())
