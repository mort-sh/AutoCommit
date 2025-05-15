#!/usr/bin/env python

import subprocess
import sys


def main():
    """Run pytest with rich output formatting."""
    cmd = ["pytest", "--rich"]

    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
