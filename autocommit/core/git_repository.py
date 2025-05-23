#!/usr/bin/env python3
"""
Provides an interface for interacting with a Git repository.
"""

import contextlib  # Import contextlib needed for _get_diff_for_untracked_file
from pathlib import Path

from autocommit.utils.console import console
from autocommit.utils.git import GitResult, parse_diff_stats, run_git_command


class GitRepositoryError(Exception):
    """Custom exception for Git repository errors."""

    pass


class GitRepository:
    """Represents a Git repository and provides methods for interaction."""

    def __init__(self, path: str | Path | None = None):
        """
        Initializes the GitRepository.

        Args:
            path: The path to the repository root. Defaults to the current working directory.
        """
        self.path = Path(path) if path else Path.cwd()
        if not self._is_valid_repository():
            raise GitRepositoryError(f"'{self.path}' is not a valid Git repository.")

    def _run_command(self, command: list[str]) -> GitResult:
        """Helper to run git commands within the repository context."""
        return run_git_command(command, cwd=self.path)

    def _is_valid_repository(self) -> bool:
        """Check if the path is a valid Git repository."""
        result = self._run_command(["git", "rev-parse", "--is-inside-work-tree"])
        return result["error"] is None and result["stdout"] == "true"

    def get_current_branch(self) -> str:
        """Gets the current active branch name."""
        result = self._run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        if result["error"]:
            raise GitRepositoryError(f"Failed to get current branch: {result['error']}")
        if not result["stdout"]:
            raise GitRepositoryError("Failed to get current branch: No branch name returned.")
        return result["stdout"]  # Correct key is stdout

    def push(self, remote: str = "origin", branch: str | None = None) -> None:
        """
        Pushes commits to the remote repository.

        Args:
            remote: The name of the remote repository (default: "origin").
            branch: The branch to push to. If None, pushes the current branch.

        Raises:
            GitRepositoryError: If getting the current branch fails or the push command fails.
        """
        try:
            # get_current_branch now raises error if it fails
            target_branch = branch or self.get_current_branch()

            result = self._run_command(["git", "push", remote, target_branch])

            # Check for errors, ignoring "Everything up-to-date" which is not a failure
            # Raise error unless it's the specific "up-to-date" message
            if result["error"] and "Everything up-to-date" not in result["error"]:
                raise GitRepositoryError(
                    f"Failed to push to {remote}/{target_branch}: {result['error']}"
                )
            elif result["error"]:  # Log the "up-to-date" message if present
                console.print(f"Push info: {result['error']}", style="info")

            # Log warnings if any
            if result["warnings"]:
                for warning in result["warnings"]:
                    console.print(
                        f"Git warning during push: {warning['type']} - {warning['file']}",
                        style="warning",
                    )

            # No return value needed, success means no exception raised
        except GitRepositoryError:  # Re-raise specific errors
            raise
        except Exception as e:  # Wrap unexpected errors
            raise GitRepositoryError(f"An unexpected error occurred during push: {e}") from e

    def _parse_git_status_line(self, line: str) -> tuple[str, str]:
        """Parse a git status line to extract status and file path."""
        # Note: Debug logging removed, should be handled by caller if needed
        if not line.strip():
            return "", ""

        status = line[:2].strip()
        parts = line.strip().split(" ", 1)
        file_path = parts[1].strip() if len(parts) > 1 else ""

        # Handle renamed files
        if status == "R" and " -> " in file_path:
            _, new_path = file_path.split(" -> ")
            file_path = new_path
        elif status == "R":
            # This is just a parsing warning, not critical failure
            console.print(
                f"Warning: Unable to parse renamed file format: {file_path}", style="warning"
            )

        return status, file_path

    def get_status(self) -> list[dict[str, str]]:
        """
        Gets the status of the repository using 'git status --porcelain'.

        Returns:
            A list of dictionaries, each containing 'status' and 'path' for a changed file.
            Raises GitRepositoryError if the command fails.
        """
        result = self._run_command(["git", "status", "--porcelain"])
        if result["error"]:
            raise GitRepositoryError(f"Failed to get git status: {result['error']}")

        # Log warnings if any (e.g., line ending warnings)
        if result["warnings"]:
            for warning in result["warnings"]:
                console.print(
                    f"Git warning: {warning['type']} - {warning['file']}", style="warning"
                )

        files_status = []
        for line in result["stdout"].splitlines():
            if not line.strip():
                continue
            status, file_path = self._parse_git_status_line(line)
            if status and file_path:
                files_status.append({"status": status, "path": file_path})

        return files_status

    def add_to_gitignore(self, file_pattern: str) -> bool:
        """
        Adds a pattern to the .gitignore file in the repository root.

        Returns:
            True if pattern was added or already exists, False otherwise.

        Raises:
            GitRepositoryError: If writing to .gitignore fails unexpectedly.
        """
        gitignore_path = self.path / ".gitignore"
        try:
            # Ensure correct pattern format (e.g., trailing slash for directories)
            # Use absolute path temporarily for is_dir check
            pattern_to_add = file_pattern  # Keep original for messages
            abs_path = self.path / file_pattern
            # Need to handle potential errors if path doesn't exist or is not accessible
            is_dir = False
            try:
                if abs_path.exists() and abs_path.is_dir():
                    is_dir = True
            except OSError as e:
                console.print(
                    f"Warning: Could not check if {file_pattern} is a directory: {e}",
                    style="warning",
                )
                # Assume not a directory if check fails
                is_dir = False

            if is_dir and not file_pattern.endswith("/"):
                pattern = f"{file_pattern}/"
            else:
                pattern = file_pattern

            content = ""
            if gitignore_path.exists():
                try:
                    content = gitignore_path.read_text(encoding="utf-8")
                except OSError as e:
                    raise GitRepositoryError(f"Failed to read .gitignore: {e}") from e

            # Only add if not already present
            # Check for exact line match or pattern within existing lines
            pattern_exists = False
            # Handle both exact match and match ignoring leading/trailing whitespace
            for line in content.splitlines():
                if line.strip() == pattern:
                    pattern_exists = True
                    break
            # Also check with added newlines for robust matching
            if not pattern_exists:
                pattern_exists = f"\n{pattern}\n" in f"\n{content}\n"

            if not pattern_exists:
                with gitignore_path.open("a", encoding="utf-8") as f:
                    # Add a newline before the pattern if the file doesn't end with one
                    if content and not content.endswith("\n"):
                        f.write("\n")
                    f.write(f"{pattern}\n")
                console.print(
                    f"Added '{pattern_to_add}' to .gitignore", style="success"
                )  # Keep console for now
                return True  # Added successfully
            else:
                # console.print(f"Pattern '{pattern}' already in .gitignore", style="info") # Optional info message
                return True  # Consider it success if already present

        except OSError as e:
            # Raise specific error for file system issues
            raise GitRepositoryError(f"Failed to write to .gitignore: {e}") from e
        except Exception as e:
            # Catch other unexpected errors during the process
            console.print(
                f"Warning: Unexpected error checking/adding '{pattern_to_add}' to .gitignore: {e}",
                style="warning",
            )
            # Return False for unexpected non-OS errors, as the state is uncertain
            return False

    def _get_diff_for_untracked_file(self, file_path: str) -> tuple[str, tuple[int, int]]:
        """Gets the diff content for an untracked file."""
        abs_path = self.path / file_path
        try:
            is_dir = False
            with contextlib.suppress(Exception):  # Use contextlib from files.py import
                is_dir = abs_path.is_dir()

            if is_dir:
                return f"New directory: {file_path}/", (1, 0)
            else:
                # Read content relative to repository path
                content = abs_path.read_text(encoding="utf-8", errors="replace")
                line_count = content.count("\n") + (
                    1 if content and not content.endswith("\n") else 0
                )
                return f"New file: {file_path}\n\n{content}", (line_count, 0)
        except PermissionError:
            console.print(f"Notice: Permission denied reading {file_path}", style="warning")
            return f"New file: {file_path} (Permission denied)", (1, 0)
        except Exception as e:
            console.print(f"Error reading untracked file {file_path}: {e}", style="warning")
            return "New file (could not read content)", (1, 0)

    def get_diff(self, file_path: str, status: str) -> tuple[str, tuple[int, int]]:
        """
        Gets the diff for a specific file based on its status.

        Args:
            file_path: The path of the file relative to the repository root.
            status: The Git status code (e.g., 'M', 'A', 'D', '??').

        Returns:
            A tuple containing the diff string and a tuple of (added_lines, deleted_lines).
            Raises GitRepositoryError on failure to run git commands.
        """
        if status.startswith("D"):
            return "File was deleted", (0, -1)  # Represent deletion stats distinctly
        elif status == "??":
            return self._get_diff_for_untracked_file(file_path)
        else:
            # Get diff stats
            # Use relative path for git commands
            diff_stats_result = self._run_command(["git", "diff", "--shortstat", file_path])
            if diff_stats_result["error"]:
                raise GitRepositoryError(
                    f"Failed to get diff stats for {file_path}: {diff_stats_result['error']}"
                )

            plus_minus = parse_diff_stats(diff_stats_result["stdout"])

            # Get actual diff
            diff_result = self._run_command(["git", "diff", file_path])
            if diff_result["error"]:
                # Log warning but don't raise, return stats if available
                console.print(
                    f"Warning: Failed to get full diff content for {file_path}: {diff_result['error']}",
                    style="warning",
                )
                return "Error getting diff content", plus_minus

            return diff_result["stdout"], plus_minus

    def stage_files(self, file_paths: list[str]) -> None:
        """
        Stages the specified files using 'git add'.

        Args:
            file_paths: A list of file paths relative to the repository root.

        Raises:
            GitRepositoryError: If staging fails.
        """
        if not file_paths:
            return True  # Nothing to stage

        command = ["git", "add", "--"] + file_paths
        result = self._run_command(command)

        if result["error"]:
            raise GitRepositoryError(
                f"Failed to stage files ({', '.join(file_paths)}): {result['error']}"
            )
        # Log warnings if any
        if result["warnings"]:
            for warning in result["warnings"]:
                console.print(
                    f"Git warning during stage: {warning['type']} - {warning['file']}",
                    style="warning",
                )

        # Success means no exception was raised

    def commit(self, message: str) -> str | None:
        """
        Creates a commit with the given message.

        Args:
            message: The commit message.

        Returns:
            The short commit hash if successful. Returns None if nothing to commit.

        Raises:
            GitRepositoryError: If the commit command fails for reasons other than 'nothing to commit'.
        """
        command = ["git", "commit", "-m", message]
        result = self._run_command(command)

        if result["error"]:
            # Handle specific non-error cases like "nothing to commit"
            if "nothing to commit" in result["error"]:
                console.print("Nothing to commit, working tree clean.", style="info")
                return None  # Or indicate no commit needed? Returning None for now.
            elif "no changes added to commit" in result["error"]:
                console.print("No changes added to commit.", style="info")
                return None

            # Raise error for actual commit failures
            raise GitRepositoryError(f"Failed to create commit: {result['error']}")

        # Log warnings if any
        if result["warnings"]:
            for warning in result["warnings"]:
                console.print(
                    f"Git warning during commit: {warning['type']} - {warning['file']}",
                    style="warning",
                )

        # Get the hash of the new commit
        hash_result = self._run_command(["git", "rev-parse", "--short", "HEAD"])
        if hash_result["error"]:
            # Log warning but don't fail the whole operation
            console.print(
                f"Warning: Commit successful, but failed to get commit hash: {hash_result['error']}",
                style="warning",
            )
            return "Success (hash unavailable)"

        return hash_result["stdout"]

    def get_repository_name(self) -> str:
        """Gets the name of the repository directory."""
        return self.path.name

    # --- Other methods to be added ---
