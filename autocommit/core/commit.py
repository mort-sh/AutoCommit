#!/usr/bin/env python3
"""
Commit and push functionality for git repository changes.
"""


from autocommit.utils.console import console
from autocommit.utils.git import run_git_command

# commit_file function removed as commit logic is now centralized in processor.py


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
