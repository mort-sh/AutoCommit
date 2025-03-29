#!/usr/bin/env python3
"""
File processing functionality for git repository changes.
"""

import argparse
import contextlib
import os
from pathlib import Path
from typing import Any

from autocommit.utils.console import console
from autocommit.utils.file import is_binary
from autocommit.utils.git import parse_diff_stats, run_git_command


def prompt_for_untracked_file(file_path: str, add_all_selected: bool = False) -> str:
    """
    Prompt the user for what to do with an untracked file.

    Args:
        file_path: Path to the untracked file
        add_all_selected: Whether the user has already selected "Add All"

    Returns:
        Action to take: "add", "ignore", "skip", or "add_all"
    """
    if add_all_selected:
        return "add"

    while True:
        console.print(f"\nUntracked file: [bold]{file_path}[/bold]")
        choice = (
            console.input(
                "[A]dd file, [I]gnore file (add to .gitignore), [S]kip file, "
                "or [AA] Add all untracked files: "
            )
            .strip()
            .lower()
        )

        if choice in ["a", "add"]:
            return "add"
        elif choice in ["i", "ignore"]:
            return "ignore"
        elif choice in ["s", "skip"]:
            return "skip"
        elif choice in ["aa", "add all"]:
            return "add_all"
        else:
            console.print("Invalid choice, please try again.", style="warning")


def add_to_gitignore(file_path: str) -> bool:
    """Add a file pattern to .gitignore file."""
    try:
        # Ensure we add the correct pattern - for directories, add trailing slash
        if os.path.isdir(file_path) and not file_path.endswith("/"):
            pattern = f"{file_path}/"
        else:
            pattern = file_path

        with open(".gitignore", "a+") as f:
            # Move to the beginning of the file to check if it exists already
            f.seek(0)
            content = f.read()

            # Only add if not already in .gitignore
            if pattern not in content:
                # Add a newline before the pattern if needed
                if not content.endswith("\n") and content:
                    f.write("\n")
                f.write(f"{pattern}\n")

        console.print(f"Added {pattern} to .gitignore", style="success")
        return True
    except Exception as e:
        console.print(f"Error adding to .gitignore: {e}", style="warning")
        return False


def _parse_git_status_line(line: str, debug: bool = False) -> tuple[str, str]:
    """Parse a git status line to extract status and file path."""
    if not line.strip():
        return "", ""

    # Parse the status output
    status = line[:2].strip()

    # Get the file path - handle the different formats of git status porcelain output
    parts = line.strip().split(" ", 1)
    file_path = parts[1].strip() if len(parts) > 1 else ""

    if debug:
        console.print(f"Parsed status: '{status}', file_path: '{file_path}'", style="file_header")

    # Handle renamed files
    if status == "R" and " -> " in file_path:
        old_path, new_path = file_path.split(" -> ")
        file_path = new_path
    elif status == "R":
        console.print(f"Warning: Unable to parse renamed file format: {file_path}", style="warning")

    return status, file_path


def _collect_untracked_files(stdout: str, debug: bool = False) -> list[str]:
    """Collect all untracked files from git status output."""
    untracked_files = []

    for line in stdout.splitlines():
        status, file_path = _parse_git_status_line(line, debug)

        # Collect untracked files for user prompting
        if status == "??":
            untracked_files.append(file_path)

    return untracked_files


def _process_untracked_files(untracked_files: list[str], add_all_untracked: bool) -> set[str]:
    """Process untracked files with user prompts and return skipped files."""
    skipped_files = set()

    for file_path in untracked_files:
        file_path_obj = Path(file_path)

        # Check if the file is a directory
        is_dir = False
        try:
            is_dir = file_path_obj.is_dir()
        except PermissionError:
            # Assume it's not a directory if we can't check
            is_dir = False

        # Skip directories automatically or handle with special prompt
        if is_dir:
            console.print(f"Detected directory: {file_path}/", style="file_header")
            # We can skip prompting for directories - git will handle adding all contents

        # Prompt the user for what to do with this untracked file
        action = (
            "add" if add_all_untracked else prompt_for_untracked_file(file_path, add_all_untracked)
        )

        if action == "add_all":
            add_all_untracked = True
            action = "add"

        if action == "ignore":
            add_to_gitignore(file_path)
            skipped_files.add(file_path)
        elif action == "skip":
            console.print(f"Skipping {file_path}", style="warning")
            skipped_files.add(file_path)

    return skipped_files


def _get_diff_for_file(status: str, file_path: str) -> tuple[str, tuple[int, int]]:
    """Get the diff for a file based on its status."""
    if status.startswith("D"):
        # File was deleted
        return "File was deleted", (0, -1)  # Placeholder
    elif status == "??":
        return _get_diff_for_untracked_file(file_path)
    else:
        # Get the diff stats
        diff_stats, _ = run_git_command(["git", "diff", "--shortstat", file_path])
        plus_minus = parse_diff_stats(diff_stats)

        # Get the actual diff
        diff, _ = run_git_command(["git", "diff", file_path])
        return diff, plus_minus


def _get_diff_for_untracked_file(file_path: str) -> tuple[str, tuple[int, int]]:
    """Get the diff for an untracked file."""
    try:
        # Check if it's a directory
        is_dir = False
        with contextlib.suppress(Exception):
            is_dir = os.path.isdir(file_path)

        if is_dir:
            # For directories, just use a placeholder
            return f"New directory: {file_path}/", (1, 0)  # Placeholder
        else:
            # For regular files, try to read content
            with open(file_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
            line_count = content.count("\n") + (0 if content.endswith("\n") else 1)
            return f"New file: {file_path}\n\n{content}", (line_count, 0)  # All lines are additions
    except PermissionError:
        # For permission errors, just use a placeholder diff
        console.print(
            f"Notice: Permission denied reading {file_path}, will still attempt to commit",
            style="warning",
        )
        return f"New file: {file_path} (Permission denied, but will be committed)", (1, 0)
    except Exception as e:
        console.print(f"Error reading untracked file {file_path}: {e}", style="warning")
        return "New file (could not read content)", (1, 0)


def _check_file_exists(file_path: str, status: str) -> bool:
    """Check if a file exists and handle errors appropriately."""
    file_path_obj = Path(file_path)
    try:
        file_exists = file_path_obj.exists()
        if not file_exists and not status.startswith("D"):
            # For untracked files (??), this is an error since the file should exist
            # For other statuses, it might be a git status inconsistency
            if status == "??":
                console.print(f"Error: Untracked file {file_path} not found", style="warning")
            else:
                console.print(f"Warning: File {file_path} does not exist", style="warning")
            return False
        return True
    except PermissionError:
        # If we get a permission error checking existence, assume file exists
        # Git can still access and commit these files
        console.print(
            f"Notice: Permission check failed for {file_path}, treating as accessible",
            style="warning",
        )
        return True


def _is_binary_file(file_path: str, file_path_obj: Path) -> bool:
    """Determine if a file is binary."""
    try:
        return is_binary(file_path_obj) if not os.path.isdir(file_path) else False
    except Exception:  # Specify Exception instead of bare except
        # If we can't determine binary status, assume it's not binary
        return False


def get_uncommitted_files(args: argparse.Namespace | None = None) -> list[dict[str, Any]]:
    """Get all uncommitted files in the repository."""
    # Get the status of the repository
    stdout, stderr = run_git_command(["git", "status", "--porcelain"])
    if stderr:
        console.print(f"Error getting git status: {stderr}", style="warning")
        return []

    # Default args if none provided
    if args is None:
        args = argparse.Namespace(debug=False, auto_track=False)

    # Set up for tracking untracked file decisions
    add_all_untracked = args.auto_track if hasattr(args, "auto_track") else False
    debug = args.debug if hasattr(args, "debug") else False

    # First, collect all untracked files and prompt the user
    untracked_files = _collect_untracked_files(stdout, debug)

    # Process untracked files first with user prompts
    skipped_files = _process_untracked_files(untracked_files, add_all_untracked)

    # Now process all files for actual diff and staging
    files = []
    for line in stdout.splitlines():
        if not line.strip():
            continue

        status, file_path = _parse_git_status_line(line, debug)

        if debug:
            console.print(f"Git status line: '{line}'", style="file_header")

        # Skip files that the user chose to ignore or skip
        if file_path in skipped_files:
            continue

        # Check if file exists (except for deleted files)
        if not _check_file_exists(file_path, status):
            continue

        # Get the diff for the file
        diff, plus_minus = _get_diff_for_file(status, file_path)

        # Check if the file is binary
        file_path_obj = Path(file_path)
        is_binary_file = _is_binary_file(file_path, file_path_obj)

        files.append({
            "path": file_path,
            "status": status,
            "diff": diff if not is_binary_file else "Binary file",
            "is_binary": is_binary_file,
            "plus_minus": plus_minus,
        })

    return files
