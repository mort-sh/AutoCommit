#!/usr/bin/env python3
"""
Commit and push functionality for git repository changes.
"""

from pathlib import Path

from autocommit.utils.console import console
from autocommit.utils.git import run_git_command


def commit_file(
    file_path: str, message: str, file_status: str = "", test_mode: bool = False
) -> bool:
    """Commit a file with the given message."""
    try:
        if test_mode:
            return True

        # Check if file exists before attempting to stage it (except for deleted files)
        try:
            if not Path(file_path).exists() and not (file_status and file_status.startswith("D")):
                console.print(f"Error staging {file_path}: File does not exist", style="warning")
                return False
        except PermissionError:
            # If we get a permission error checking file existence, continue anyway
            # Git can still stage and commit files even if Python doesn't have permissions
            console.print(
                f"Notice: Permission check failed for {file_path}, will still attempt to stage",
                style="warning",
            )
            # Continue with the staging process

        # Stage the file - use different Git commands based on file status
        if file_status and file_status.startswith("D"):
            # For deleted files, use git rm
            stage_output, stage_error = run_git_command(["git", "rm", file_path])
        else:
            # For other files, use git add
            stage_output, stage_error = run_git_command(["git", "add", file_path])

        if (
            stage_error
            and "warning:" not in stage_error
            and "LF will be replaced by CRLF" not in stage_error
        ):
            console.print(f"Error staging {file_path}: {stage_error}", style="warning")
            return False
        elif stage_error:
            # Just print warnings but continue
            console.print(f"Warning staging {file_path}: {stage_error}", style="warning")

        # Create the commit
        commit_output, commit_error = run_git_command([
            "git",
            "commit",
            "-m",
            message,
        ])
        if commit_error and "nothing to commit" not in commit_error:
            console.print(f"Error committing {file_path}: {commit_error}", style="warning")
            return False

        return True
    except Exception as e:
        console.print(f"Error in commit process: {e}", style="warning")
        return False


def push_commits(remote: str = "origin", branch: str = "", test_mode: bool = False) -> bool:
    """Push the commits to the remote repository."""
    try:
        if test_mode:
            if branch:
                console.print(f"\nWould push to {remote}/{branch}", style="push_info")
            else:
                console.print(f"\nWould push to {remote}", style="push_info")
            return True

        # Get the current branch if none specified
        if not branch:
            branch_output, branch_error = run_git_command([
                "git",
                "rev-parse",
                "--abbrev-ref",
                "HEAD",
            ])
            if branch_error:
                console.print(f"Error getting current branch: {branch_error}", style="warning")
                return False
            branch = branch_output.strip()

        # Push to the remote
        push_output, push_error = run_git_command(["git", "push", remote, branch])
        if push_error and "Everything up-to-date" not in push_error:
            console.print(f"Error pushing to {remote}/{branch}: {push_error}", style="warning")
            return False

        return True
    except Exception as e:
        console.print(f"Error in push process: {e}", style="warning")
        return False
