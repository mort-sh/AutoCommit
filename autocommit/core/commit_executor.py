"""
Handles the execution of Git commands to apply patches and create commits.
"""

import os
from pathlib import Path
import re
import tempfile
from typing import Any

from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree

from autocommit.core.config import Config
from autocommit.core.git_repository import GitRepository, GitRepositoryError
from autocommit.utils.console import console


def apply_commits(
    repo: GitRepository,
    files_commit_data: list[list[dict[str, Any]] | None],
    files: list[dict[str, Any]],
    commit_panels_to_update: dict[tuple[int, int], Panel],  # Key is (file_idx, group_idx-1)
    tree: Tree,  # Passed to re-print if commits succeed
    config: Config,
) -> tuple[int, list[str]]:
    """
    Applies the actual commits based on the generated messages and patches.

    Args:
        repo: The GitRepository instance.
        files_commit_data: Processed data including messages and patches for each file group.
        files: Original list of changed files information.
        commit_panels_to_update: Dictionary mapping (file_idx, group_idx-1) to Rich Panels for UI update.
        tree: The Rich Tree object to potentially re-print.
        config: The application configuration object.

    Returns:
        A tuple containing:
        - The number of commits successfully made.
        - A list of relative paths for files that were successfully committed.
    """
    total_commits_made = 0
    committed_file_paths = set()  # Use set for unique paths
    console.print("\nApplying commits...", style="info")

    for file_index, commit_groups in enumerate(files_commit_data):
        if commit_groups is None:
            continue  # Skip files that failed processing

        original_file_info = files[file_index]
        path = original_file_info["path"]
        console.print(f"\nProcessing commits for [file_path]{path}[/]...", style="info")

        # Track if the index needs resetting before the *first* patch attempt for this file
        needs_initial_reset = True
        # Track if any commit succeeded for this file to update final list
        # commit_succeeded_for_file = False # This variable seems unused, removing

        for group_index_zero_based, group_data in enumerate(commit_groups):
            group_message = group_data.get("message")
            patch_content = group_data.get("patch_content")
            is_binary = group_data.get("is_binary", False)
            status = group_data.get(
                "status", ""
            )  # Get status if available (from whole_file processing)
            # Check if it was processed as a whole file (single group)
            is_whole_file_commit = group_data.get("total_hunks_in_file", 0) == 1
            group_index_one_based = group_data.get(
                "group_index", group_index_zero_based + 1
            )  # Use stored or calculate

            panel_key = (file_index, group_index_zero_based)  # Key is 0-based
            panel_to_update = commit_panels_to_update.get(panel_key)

            # --- Validate Group Data ---
            if (
                not group_message
                or "(AI Error)" in group_message
                or "(System Error)" in group_message
                or group_data.get("error")  # Check for explicit error flag
            ):
                error_reason = group_data.get("error", "Invalid Msg")
                console.print(
                    f"  Skipping Group {group_index_one_based} (error: {error_reason}).",
                    style="warning",
                )
                if panel_to_update:
                    panel_to_update.title = Text.assemble(
                        (" ", "warning"),
                        (f"Skipped ({error_reason})", "warning"),
                        (" ─── ", "commit_panel_border"),
                        ("Message ", "commit_title"),
                    )
                continue  # Skip to next group

            # --- Debug Print Patch ---
            if config.debug and patch_content:
                console.print(
                    f"\n[debug]DEBUG:[/] Applying patch for [file_path]{path}[/] - Group {group_index_one_based}:",
                    style="debug",
                )
                syntax = Syntax(patch_content, "diff", theme="default", line_numbers=True)
                console.print(syntax)
                console.print("[debug]DEBUG:[/] End of patch.", style="debug")
                # Dump the patch to a file for diagnostic purposes
                diagnostics_dir = Path("debug_patches")
                try:
                    diagnostics_dir.mkdir(exist_ok=True)
                    safe_path = path.replace("/", "_").replace("\\", "_")
                    dump_path = (
                        diagnostics_dir / f"patch_{safe_path}_group{group_index_one_based}.diff"
                    )
                    # Use binary write with UTF-8 encoding for consistency with read
                    with open(dump_path, "wb") as f:
                        f.write(patch_content.encode("utf-8"))
                    console.print(f"[debug]DEBUG:[/] Patch dumped to {dump_path}", style="debug")
                except Exception as e:
                    console.print(f"[debug]DEBUG:[/] Failed to dump patch: {e}", style="debug")

            # --- Staging Logic (Patch or Add) ---
            commit_hash = None
            stage_or_patch_error = None
            try:
                # Special handling for whole file commits (binary, deleted, single hunk/group, untracked)
                if is_binary or status.startswith("D") or status == "??" or is_whole_file_commit:
                    if needs_initial_reset:
                        console.print(
                            f"  Staging whole file {path} (status: {status}, binary: {is_binary})...",
                            style="info",
                        )
                        repo.stage_files([path])  # Stage the entire file
                        needs_initial_reset = (
                            False  # Staged, no need for patch reset logic below for this file
                        )
                    else:
                        # If not the first group (shouldn't happen for whole file but defensive)
                        console.print(
                            f"  Skipping staging for Group {group_index_one_based} (whole file changes likely staged).",
                            style="info",
                        )

                # Apply patch for multi-group modified files
                elif not patch_content:
                    stage_or_patch_error = "Patch content missing"
                    console.print(
                        f"  Skipping Group {group_index_one_based} ({stage_or_patch_error}).",
                        style="warning",
                    )
                else:
                    # Reset index before first patch attempt for this file
                    if needs_initial_reset:
                        console.print(f"  Resetting index for {path}...", style="info")
                        # Use explicit pathspec to avoid ambiguity
                        repo._run_command(["git", "reset", "HEAD", "--", path])
                        needs_initial_reset = False  # Reset done

                    console.print(
                        f"  Applying patch for Group {group_index_one_based}...", style="info"
                    )
                    # Use temp file for git apply --cached
                    temp_file_path = None  # Initialize
                    try:
                        # Preprocess the patch to normalize line endings (handle potential mixed endings)
                        processed_patch_content = patch_content.replace("\r\n", "\n").replace(
                            "\r", "\n"
                        )

                        # Normalize @@ hunk headers with proper spacing (defensive)
                        processed_patch_content = re.sub(
                            r"@@\s*(-\d+,\d+)\s+(\+\d+,\d+)\s*@@",
                            r"@@ \1 \2 @@",
                            processed_patch_content,
                        )

                        # Use binary mode write with UTF-8 encoding
                        with tempfile.NamedTemporaryFile(
                            mode="wb", delete=False, suffix=".patch"
                        ) as temp_patch_file:
                            temp_patch_file.write(processed_patch_content.encode("utf-8"))
                            temp_file_path = temp_patch_file.name

                        # Run git apply command
                        apply_result = repo._run_command([
                            "git",
                            "apply",
                            "--cached",
                            "--ignore-whitespace",  # More forgiving
                            "--recount",  # Recalculate counts
                            # "--unsafe-paths",    # Should not be needed if paths are normalized
                            "--verbose",  # Get more info on failure
                            "--",
                            temp_file_path,
                        ])

                        # Check for apply errors/warnings in the result
                        if apply_result["error"]:
                            error_msg = apply_result["error"]
                            # Check for common, potentially recoverable errors
                            if (
                                "patch does not apply" in error_msg
                                or "applied with offsets" in error_msg
                                or "already applied" in error_msg
                            ):
                                console.print(
                                    f"  Git Apply Warning (potential minor issue): {error_msg}",
                                    style="warning",
                                )
                                # Consider proceeding if only warnings/minor errors
                            elif config.debug:
                                console.print(
                                    f"[debug]DEBUG:[/] Git apply error: {error_msg}",
                                    style="debug",
                                )
                                raise GitRepositoryError(f"Failed to apply patch: {error_msg}")
                            else:
                                raise GitRepositoryError(
                                    f"Failed to apply patch: {error_msg}"
                                )  # Raise for serious errors

                        if apply_result["warnings"]:
                            for warning in apply_result["warnings"]:
                                console.print(
                                    f"  Git Apply Warning: {warning['type']} - {warning['file']}",
                                    style="warning",
                                )

                    finally:
                        # Clean up the temporary file
                        if temp_file_path and os.path.exists(temp_file_path):
                            try:
                                os.remove(temp_file_path)
                            except OSError as e:
                                console.print(
                                    f"Warning: Failed to remove temp patch file {temp_file_path}: {e}",
                                    style="warning",
                                )

                # --- Commit Attempt --- (Only if staging/patching didn't raise an error)
                if stage_or_patch_error is None:
                    console.print(
                        f"  Attempting commit for Group {group_index_one_based}...", style="info"
                    )
                    commit_hash = repo.commit(group_message)  # Commit staged changes

            except GitRepositoryError as e:
                stage_or_patch_error = f"Git Error: {e}"
                console.print(
                    f"  Error processing commit for Group {group_index_one_based}: {e}",
                    style="warning",
                )
                # Don't continue to next group for this file if fundamental error occurred
                if panel_to_update:
                    fail_title_padding_len = (
                        panel_to_update.width
                        - len(" ")
                        - len("Failed")
                        - len(str(e)[:20])  # Show part of error
                        - len("Message ")
                        - 6  # Adjust padding estimate
                    )
                    fail_title_padding = "─" * max(0, fail_title_padding_len)
                    panel_to_update.title = Text.assemble(
                        (" ", "warning"),
                        ("Failed", "warning"),
                        (f" ({str(e)[:20]}...)", "warning"),
                        (" ", "default"),
                        (fail_title_padding, "commit_panel_border"),
                        (" ", "default"),
                        ("Message ", "commit_title"),
                    )
                break  # Exit inner loop for this file

            # --- Update UI Based on Outcome --- (If commit was attempted)
            if commit_hash and commit_hash != "Success (hash unavailable)":
                total_commits_made += 1
                committed_file_paths.add(path)
                console.print(
                    f"  Committed Group {group_index_one_based} as [commit_hash]{commit_hash}[/].",
                    style="success",
                )
                if panel_to_update:
                    hash_title_padding_len = (
                        panel_to_update.width - len(" ") - len(commit_hash) - len("Message ") - 4
                    )
                    hash_title_padding = "─" * max(0, hash_title_padding_len)
                    new_title = Text.assemble(
                        (" ", "commit_title"),
                        (commit_hash, "commit_hash"),
                        (" ", "default"),
                        (hash_title_padding, "commit_panel_border"),
                        (" ", "default"),
                        ("Message ", "commit_title"),
                    )
                    panel_to_update.title = new_title

                # Reset index *after* successful commit for patch-based files
                if not (
                    is_binary or status.startswith("D") or status == "??" or is_whole_file_commit
                ):
                    try:
                        console.print(f"  Resetting index for {path} post-commit...", style="info")
                        repo._run_command(["git", "reset", "HEAD", "--", path])
                    except GitRepositoryError as e:
                        console.print(
                            f"  Warning: Failed to reset index for {path} after commit: {e}",
                            style="warning",
                        )
                        # Log warning but continue processing other groups/files

            elif commit_hash == "Success (hash unavailable)":
                total_commits_made += 1
                committed_file_paths.add(path)
                console.print(
                    f"  Committed Group {group_index_one_based} (hash unavailable).",
                    style="success",
                )
                if panel_to_update:
                    na_hash = "{HASH N/A}"
                    na_title_padding_len = (
                        panel_to_update.width - len(" ") - len(na_hash) - len("Message ") - 4
                    )
                    na_title_padding = "─" * max(0, na_title_padding_len)
                    new_title = Text.assemble(
                        (" ", "commit_title"),
                        (na_hash, "commit_hash"),
                        (" ", "default"),
                        (na_title_padding, "commit_panel_border"),
                        (" ", "default"),
                        ("Message ", "commit_title"),
                    )
                    panel_to_update.title = new_title
                # Reset index *after* successful commit for patch-based files
                if not (
                    is_binary or status.startswith("D") or status == "??" or is_whole_file_commit
                ):
                    try:
                        console.print(f"  Resetting index for {path} post-commit...", style="info")
                        repo._run_command(["git", "reset", "HEAD", "--", path])
                    except GitRepositoryError as e:
                        console.print(
                            f"  Warning: Failed to reset index for {path} after commit: {e}",
                            style="warning",
                        )

            # Handle cases where commit didn't happen or failed
            else:
                skip_reason = "Commit Skipped"  # Default if no error and no hash
                if (
                    commit_hash is None and stage_or_patch_error is None
                ):  # Commit returned None (nothing to commit)
                    skip_reason = "Nothing to Commit"
                elif stage_or_patch_error:
                    skip_reason = f"Failed ({stage_or_patch_error[:20]}...)"

                console.print(
                    f"  Skipped commit for Group {group_index_one_based} ({skip_reason}).",
                    style="info" if skip_reason == "Nothing to Commit" else "warning",
                )
                if panel_to_update:
                    icon = " " if skip_reason == "Nothing to Commit" else " "
                    style = "info" if skip_reason == "Nothing to Commit" else "warning"
                    skip_title_padding_len = (
                        panel_to_update.width - len(icon) - len(skip_reason) - len("Message ") - 4
                    )
                    skip_title_padding = "─" * max(0, skip_title_padding_len)
                    panel_to_update.title = Text.assemble(
                        (icon, style),
                        (skip_reason, style),
                        (" ", "default"),
                        (skip_title_padding, "commit_panel_border"),
                        (" ", "default"),
                        ("Message ", "commit_title"),
                    )
                # If commit fails or is skipped, we might still need to reset the index
                # if a patch was attempted but didn't result in a commit.
                # Reset only if it's a patch-based file and the failure wasn't the reset itself.
                if (
                    not needs_initial_reset
                    and not (
                        is_binary
                        or status.startswith("D")
                        or status == "??"
                        or is_whole_file_commit
                    )
                    and "reset index" not in skip_reason
                ):
                    try:
                        console.print(
                            f"  Resetting index for {path} after skipped/failed commit...",
                            style="info",
                        )
                        repo._run_command(["git", "reset", "HEAD", "--", path])
                    except GitRepositoryError as e:
                        console.print(
                            f"  Warning: Failed to reset index for {path} after skipped/failed commit: {e}",
                            style="warning",
                        )
                        # If reset fails here, subsequent groups for this file might be problematic. Break.
                        break  # Safer to stop processing this file if reset fails

    # Re-print the tree if commits were made to show updated hashes/statuses
    if total_commits_made > 0:
        console.print("\nCommit tree updated:")
        console.print(tree)
        console.print("\n")

    return total_commits_made, list(committed_file_paths)  # Convert set back to list
