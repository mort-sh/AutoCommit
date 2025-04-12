#!/usr/bin/env python3
"""
Utility functions for Git operations.
"""

import re
import subprocess
from typing import Any, TypedDict


class GitWarning(TypedDict):
    type: str
    file: str
    details: dict[str, Any]


class GitResult(TypedDict):
    stdout: str
    stderr: str  # Raw stderr
    warnings: list[GitWarning]
    error: str | None  # Critical errors


def _parse_git_warnings(stderr: str) -> tuple[list[GitWarning], str]:
    """Parse known warnings from git stderr, returning warnings and remaining stderr."""
    warnings: list[GitWarning] = []
    remaining_stderr_lines = []
    crlf_pattern = re.compile(
        r"warning: in the working copy of '(.+)', LF will be replaced by CRLF"
    )

    for line in stderr.splitlines():
        crlf_match = crlf_pattern.match(line)
        if crlf_match:
            warnings.append({
                "type": "LineEndingLFtoCRLF",
                "file": crlf_match.group(1),
                "details": {"from": "LF", "to": "CRLF"},
            })
        # Add other warning patterns here if needed
        # elif other_pattern.match(line):
        #     ...
        else:
            remaining_stderr_lines.append(line)

    return warnings, "\n".join(remaining_stderr_lines)


def run_git_command(command: list[str], cwd=None) -> GitResult:
    """Run a git command and return a structured result including parsed warnings."""
    result: GitResult = {"stdout": "", "stderr": "", "warnings": [], "error": None}
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate()
        result["stdout"] = stdout.strip()
        result["stderr"] = stderr.strip()  # Store raw stderr

        # Parse warnings from raw stderr
        parsed_warnings, remaining_stderr = _parse_git_warnings(result["stderr"])
        result["warnings"] = parsed_warnings

        # Treat remaining stderr as potential error if process failed or it's not empty
        if process.returncode != 0 and remaining_stderr:
            result["error"] = remaining_stderr
        elif remaining_stderr:
            # If process succeeded but there's still stderr, maybe treat as non-critical error or just log?
            # For now, let's put it in error field if it exists.
            result["error"] = remaining_stderr

    except subprocess.SubprocessError as e:
        result["error"] = f"Subprocess error executing git command: {e}"
    except FileNotFoundError:
        result["error"] = f"Error: Command '{command[0]}' not found. Is Git installed and in PATH?"
    except Exception as e:
        result["error"] = f"Unexpected error executing git command: {e}"

    return result


def parse_diff_stats(diff_stats: str) -> tuple[int, int]:
    """Parse the diff stats to get the number of added and deleted lines."""
    additions = re.search(r"(\d+) insertion", diff_stats)
    deletions = re.search(r"(\d+) deletion", diff_stats)

    plus = int(additions.group(1)) if additions else 0
    minus = int(deletions.group(1)) if deletions else 0

    return (plus, minus)


def is_git_repository(cwd=None) -> bool:
    """
    Check if the given directory (or current working directory if None) is inside a Git repository.

    Args:
        cwd: The directory path to check. Defaults to the current working directory.

    Returns:
        True if the directory is a Git repository, False otherwise.
    """
    command = ["git", "rev-parse", "--is-inside-work-tree"]
    result = run_git_command(command, cwd=cwd)

    # Check for successful execution and specific output "true"
    return result["error"] is None and result["stdout"] == "true"
