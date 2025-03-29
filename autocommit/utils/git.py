#!/usr/bin/env python3
"""
Utility functions for Git operations.
"""

import re
import subprocess


def run_git_command(command: list[str], cwd=None) -> tuple[str, str]:
    """Run a git command and return stdout and stderr."""
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
        )
        stdout, stderr = process.communicate()
        return stdout.strip(), stderr.strip()
    except subprocess.SubprocessError as e:
        return "", f"Error executing git command: {e}"


def parse_diff_stats(diff_stats: str) -> tuple[int, int]:
    """Parse the diff stats to get the number of added and deleted lines."""
    additions = re.search(r"(\d+) insertion", diff_stats)
    deletions = re.search(r"(\d+) deletion", diff_stats)

    plus = int(additions.group(1)) if additions else 0
    minus = int(deletions.group(1)) if deletions else 0

    return (plus, minus)
