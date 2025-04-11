#!/usr/bin/env python3
"""
File processing functionality for git repository changes.
"""

# import argparse -> No longer used
# import contextlib -> No longer used
import os # Still used by _is_binary_file indirectly via os.path.isdir
from pathlib import Path
from typing import Any, List, Dict, Set

from autocommit.core.config import Config
from autocommit.core.git_repository import GitRepository # GitRepositoryError not handled here
from autocommit.utils.console import console
from autocommit.utils.file import is_binary
# Removed commented out import


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


# add_to_gitignore function moved to GitRepository class

# _parse_git_status_line function moved to GitRepository class


# _collect_untracked_files is no longer needed as GitRepository.get_status() provides this info


def _process_untracked_files(
    repo: GitRepository, untracked_files: List[Dict[str, str]], config: Config
) -> Set[str]: # Replaced add_all_untracked with config
    """
    Process untracked files using prompts and GitRepository.

    Args:
        repo: The GitRepository instance.
        untracked_files: List of dictionaries [{'status': '??', 'path': file_path}, ...].
        config: The application configuration object.

    Returns:
        A set of file paths that should be skipped.
    """
    skipped_files = set()

    for file_info in untracked_files:
        file_path = file_info["path"]
        # Use absolute path for is_dir check via repo path
        file_path_obj = repo.path / file_path

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
        # Determine if we should auto-add based on config
        should_auto_add = config.auto_track or (config.test_mode is not None)
        action = (
            "add" if should_auto_add else prompt_for_untracked_file(file_path, should_auto_add)
        )

        if action == "add_all":
            # No need to track add_all_untracked separately, config handles it
            pass # Action is already 'add'
            action = "add"

        if action == "ignore":
            if repo.add_to_gitignore(file_path): # Use repo method
                 skipped_files.add(file_path)
            # If adding to gitignore fails, we don't skip, let it proceed? Or should we skip?
            # For now, only skip if successfully added to .gitignore
        elif action == "skip":
            console.print(f"Skipping {file_path}", style="warning")
            skipped_files.add(file_path)

    return skipped_files


# _get_diff_for_file function moved to GitRepository class
# _get_diff_for_untracked_file function moved to GitRepository class


def _check_file_exists(repo: GitRepository, file_path: str, status: str) -> bool:
    """Check if a file exists relative to the repo root."""
    # Construct path relative to repository root
    file_path_obj = repo.path / file_path
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
        return is_binary(file_path_obj) if not file_path_obj.is_dir() else False
    except Exception:  # Specify Exception instead of bare except
        # If we can't determine binary status, assume it's not binary
        return False


def get_uncommitted_files(repo: GitRepository, config: Config) -> List[Dict[str, Any]]: # Added repo argument
    """
    Gets all uncommitted files, handles untracked files, and retrieves their diffs.

    Args:
        repo: An initialized GitRepository object.
        config: The application configuration object.

    Returns:
        A list of dictionaries, each representing a file with its status, diff, etc.
    """
    # Removed repo instantiation, it's now passed in

    # Get status using the repository object
    try:
        all_statuses = repo.get_status()
    except GitRepositoryError as e:
        console.print(f"Error getting repository status: {e}", style="warning")
        return []
    if not all_statuses:
        console.print("No changes detected in the repository.", style="info")
        return []

    # No need for default args, config is required
    # Debug flag is now in config, but not used directly in this function anymore

    # Separate untracked files for processing
    untracked_files_info = [f for f in all_statuses if f["status"] == "??"]
    other_files_info = [f for f in all_statuses if f["status"] != "??"]

    # Process untracked files (prompting, adding to .gitignore)
    skipped_files = _process_untracked_files(repo, untracked_files_info, config) # Pass config

    # Now process all files for actual diff and staging
    # Combine remaining tracked and untracked (if not skipped) files
    processed_files_info = other_files_info + [
        f for f in untracked_files_info if f["path"] not in skipped_files
    ]

    files_data = []
    for file_info in processed_files_info:
        status = file_info["status"]
        file_path = file_info["path"]

        # Debug logging for status line removed, handled elsewhere if needed

        # Skip files that the user chose to ignore or skip
        # This check might be redundant now as skipped files are filtered earlier,
        # but keep for safety unless confirmed unnecessary.
        # if file_path in skipped_files:
        #     continue

        # Check if file exists (except for deleted files)
        if not _check_file_exists(repo, file_path, status): # Pass repo object
            continue

        # Get the diff using the repository object
        diff, plus_minus = repo.get_diff(file_path, status)

        # Check if the file is binary
        # Check if binary using absolute path
        file_path_obj = repo.path / file_path
        is_binary_file = _is_binary_file(file_path, file_path_obj) # Pass relative path for logging

        files_data.append({
            "path": file_path,
            "status": status,
            "diff": diff if not is_binary_file else "Binary file",
            "is_binary": is_binary_file,
            "plus_minus": plus_minus,
        })

    return files_data
