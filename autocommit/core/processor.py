#!/usr/bin/env python3
"""
Main processing module for AutoCommit.
"""

# import argparse -> No longer used
import concurrent.futures
import os
import textwrap
import threading
from typing import Any

from rich.box import ROUNDED
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from autocommit.core.ai import (
    OpenAIError,
    classify_hunks,
    generate_commit_message,
)  # Import OpenAIError
from autocommit.core.commit_executor import apply_commits  # Import commit execution function
from autocommit.core.config import Config  # Import Config
from autocommit.core.diff import split_diff_into_chunks
from autocommit.core.git_repository import GitRepository, GitRepositoryError
from autocommit.utils.console import (
    FILE_ICON,
    GIT_ICON,
    console,
    render_repository_preview,  # Import the new function
    # get_terminal_width, -> No longer used
    # Old print functions removed
)  # Import icons

# from autocommit.utils.git import run_git_command # No longer needed directly here


# Function to create a valid patch string from a subset of hunks of a full diff
def _create_patch_for_group(full_diff: str, group_hunks: list[dict[str, Any]]) -> str:
    """
    Creates a valid Git patch string containing only the specified hunks from a full diff.

    Args:
        full_diff: The complete diff string for the file (relative to HEAD).
        group_hunks: A list of hunk dictionaries belonging to the target group.
                     Each hunk dict must contain at least the 'diff' key.

    Returns:
        A string formatted as a Git patch, or an empty string if no hunks are provided
        or the header cannot be extracted.
    """
    if not group_hunks:
        return ""

    # Extract the header lines (diff --git, index, ---, +++) from the full diff
    header_lines = []
    lines = full_diff.splitlines()
    for line in lines:
        if (
            line.startswith("diff --git")
            or line.startswith("index ")
            or line.startswith("--- ")
            or line.startswith("+++ ")
        ):
            header_lines.append(line)
        elif line.startswith("@@"):
            break  # Stop header extraction once hunks start
    header = "\n".join(header_lines)

    if not header:
        console.print(
            f"[debug]Warning:[/] Could not extract header from diff:\n{full_diff[:200]}...",
            style="warning",
        )
        # Fallback or indicate error? Return empty for now, caller should handle.
        return ""

    # Combine the diff content of the specified hunks
    patch_body = "\n".join(
        hunk["diff"].strip() for hunk in group_hunks
    )  # Strip ensures no extra newlines between hunks

    # Combine header and the group's hunks
    # Add a newline after header if patch_body is not empty
    full_patch = (
        header + ("\n" + patch_body if patch_body else "") + "\n"
    )  # Ensure trailing newline

    return full_patch


def _prepare_chunk_diff(chunk: dict[str, Any], chunk_level: int) -> str:
    """Prepare the diff for a chunk based on chunk level."""
    chunk_diff = chunk["diff"]

    # For level 2-3, enhance the prompt with context information
    if chunk_level >= 2 and "context" in chunk:
        context_info = f"Semantic context: {chunk['context']}\n\n"
        enhanced_diff = context_info + chunk_diff
    else:
        enhanced_diff = chunk_diff

    return enhanced_diff


def _generate_messages_parallel(
    chunks: list[dict[str, Any]], model: str, chunk_level: int, parallel_level: int = 0
) -> list[str]:
    """Generate commit messages for all chunks in parallel."""
    # Determine the number of workers based on parallel_level
    if parallel_level <= 0:
        # Auto mode: Use CPU count * 2 but limit based on chunks
        max_workers = min(len(chunks), os.cpu_count() * 2)
    else:
        # Use specified level but ensure we don't exceed chunks
        max_workers = min(len(chunks), parallel_level)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create tasks for message generation
        future_to_chunk = {
            executor.submit(
                generate_commit_message, _prepare_chunk_diff(chunk, chunk_level), model
            ): i
            for i, chunk in enumerate(chunks)
        }

        # Collect results in order
        messages = [""] * len(chunks)
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_index = future_to_chunk[future]
            try:
                messages[chunk_index] = future.result()
            except OpenAIError:  # Catch specific error
                # Error already logged by ai module
                messages[chunk_index] = "[Chore] Commit changes (AI Error)"
            except Exception as e:  # Catch other unexpected errors
                console.print(
                    f"Unexpected error generating message for chunk {chunk_index}: {e}",
                    style="warning",
                )
                messages[chunk_index] = "[Chore] Commit changes (System Error)"

    return messages


def _process_file_hunks(
    file: dict[str, Any], config: Config, repo: GitRepository
) -> list[dict[str, Any]] | None:  # Replaced individual args with config
    """
    Process hunks for a single file, group them, generate messages and patches.

    Args:
        file: File information including path, diff, and status.
        config: The application configuration object.
        repo: The GitRepository instance.

    Returns:
        List of dictionaries, each representing a commit group with its message and patch,
        or None if processing fails or no hunks are found.
    """
    path = file["path"]
    # We now get the full diff relative to HEAD from the file info
    full_diff = file["diff"]  # This should now be the full diff patch
    status = file["status"]  # Keep status for potential commit logic later

    # console.print(f"Processing file: {path}", style="info") # Debug print

    # Skip binary files or deleted files - handle them with _process_whole_file
    # For patch application, handle deleted files here as well.
    if status.startswith("D"):
        result = _process_whole_file(file, config, repo)  # Pass repo
        return [result] if result else None
    elif full_diff == "Binary file":  # Specific check for binary
        result = _process_whole_file(file, config, repo)  # Pass repo and config
        return [result] if result else None

    # Split the diff into hunks using the original method
    hunks = split_diff_into_chunks(full_diff, config.chunk_level)  # Use config.chunk_level

    if not hunks:
        # console.print(f"No hunks found for {path}", style="warning") # Less verbose now
        # If no hunks but file is modified, treat as whole file change
        if status != "??":  # Only if not an untracked file with no content change detected
            result = _process_whole_file(file, config, repo)  # Pass repo
            return [result] if result else None
        return None  # No changes detected for untracked file

    # If there's only one hunk, process the whole file for simplicity
    if len(hunks) == 1:
        # Pass specific args instead of the whole namespace
        result = _process_whole_file(file, config, repo)  # Pass repo and config
        return [result] if result else None

    # console.print(f"Found {len(hunks)} hunks in {path}", style="info") # Less verbose

    # Classify hunks into logically related groups
    try:
        # Pass the raw hunk dictionaries as received from split_diff_into_chunks
        # classify_hunks now returns list[list[int]] (groups of hunk indices)
        hunk_groups_indices = classify_hunks(hunks, config.model, config.debug)  # Pass debug flag

        # Convert indices back to actual hunk data
        hunk_groups = []
        processed_indices = (
            set()
        )  # Keep track to avoid duplicating hunks if AI assigns to multiple groups
        for group_indices in hunk_groups_indices:
            group = []
            current_group_indices = []
            for idx in group_indices:
                if (
                    0 <= idx < len(hunks) and idx not in processed_indices
                ):  # Ensure index is valid and not already processed
                    group.append(hunks[idx])
                    processed_indices.add(idx)
                    current_group_indices.append(idx)  # Store the original index used

            if group:  # Only add non-empty groups
                # Store original indices with the group for later use if needed
                hunk_groups.append({"hunks": group, "indices": current_group_indices})

        # Add any remaining hunks that weren't assigned to any group into a final separate group
        remaining_hunks = []
        remaining_indices = []
        for idx, hunk in enumerate(hunks):
            if idx not in processed_indices:
                remaining_hunks.append(hunk)
                remaining_indices.append(idx)
        if remaining_hunks:
            if config.debug:
                console.print(
                    f"[debug]DEBUG:[/] Adding {len(remaining_hunks)} unclassified hunks to a separate group for [file_path]{path}[/].",
                    style="debug",
                )
            hunk_groups.append({"hunks": remaining_hunks, "indices": remaining_indices})

    except OpenAIError:
        # Error already logged by ai module
        console.print(
            f"Classification failed for {path}, treating as single group.", style="warning"
        )
        # Fallback: Treat all original hunks as one group
        # Structure the fallback data to match the expected format
        hunk_groups = [{"hunks": hunks, "indices": list(range(len(hunks)))}]
    except Exception as e:  # Catch other unexpected errors
        console.print(
            f"Unexpected error during hunk classification for {path}: {e}", style="warning"
        )
        # Fallback: Treat all original hunks as one group
        hunk_groups = [{"hunks": hunks, "indices": list(range(len(hunks)))}]

    if not hunk_groups:  # Handle case where classification returns empty (or failed silently)
        console.print(
            f"Warning: Hunk classification resulted in empty groups for {path}. Treating as single group.",
            style="warning",
        )
        hunk_groups = [{"hunks": hunks, "indices": list(range(len(hunks)))}]

    if config.debug:  # Use config.debug
        # Adjust debug print for the new structure
        console.print(
            f"[debug]DEBUG:[/] Classified {len(hunks)} hunks into {len(hunk_groups)} groups for [file_path]{path}[/]. Group indices: {[g['indices'] for g in hunk_groups]}",
            style="debug",
        )

    commit_data_list = []

    # Generate messages and patches for each group
    # The loop needs to iterate over the new structure: list[dict{"hunks": list[dict], "indices": list[int]}]
    for i, group_info in enumerate(hunk_groups, 1):
        group = group_info["hunks"]  # Extract the list of hunk dicts
        group_hunk_indices = group_info["indices"]  # Extract the original indices
        # console.print(f"\nProcessing hunk group {i}/{len(hunk_groups)} for {path}", style="info") # Less verbose

        # Combine the diffs from all hunks in this group for message generation prompt
        group_diff_for_prompt = "\n".join(hunk["diff"] for hunk in group)
        # group_hunk_indices is already retrieved from group_info

        # Generate a commit message for this group
        try:
            message = generate_commit_message(
                group_diff_for_prompt, config.model
            )  # Use config.model
        except OpenAIError:
            # Error already logged by ai module
            message = "[Chore] Commit changes (AI Error)"
        except Exception as e:  # Catch other unexpected errors
            console.print(
                f"Unexpected error generating message for group {i} in {path}: {e}", style="warning"
            )
            message = "[Chore] Commit changes (System Error)"

        # Create the specific patch for this group using the full diff
        group_patch_content = _create_patch_for_group(full_diff, group)

        if not group_patch_content:
            console.print(
                f"Warning: Could not generate patch for group {i} in {path}. Skipping group.",
                style="warning",
            )
            continue  # Skip this group if patch generation failed

        commit_data_list.append({
            "group_index": i,
            "total_groups": len(hunk_groups),
            "hunk_indices": group_hunk_indices,  # Store the original indices for this group
            "message": message,
            "patch_content": group_patch_content,  # Store the patch content for git apply
            "num_hunks_in_group": len(group),
            "total_hunks_in_file": len(hunks),
        })

    return commit_data_list


def _process_whole_file(
    file: dict[str, Any], config: Config, repo: GitRepository
) -> dict[str, Any] | None:  # Replaced model with config
    """
    Process a single file as a whole, generate its commit message and patch data.
    Used for binary files, deleted files, or files with only one hunk/group.

    Args:
        file: File information including path, full diff patch, and status.
        config: The application configuration object.
        repo: The GitRepository instance.

    Returns:
        A dictionary containing the commit data (message, patch, etc.),
        or None if processing fails.
    """
    path = file["path"]
    # This should now be the full diff patch relative to HEAD or deletion/binary marker
    full_diff_patch = file["diff"]
    status = file["status"]

    # Determine diff content for message generation (might differ from patch)
    # For binary/deleted, use the marker. Otherwise, use the patch content.
    diff_for_prompt = full_diff_patch
    if status.startswith("D"):
        diff_for_prompt = "File was deleted"
    elif file.get("is_binary", False):  # Check if marked as binary
        diff_for_prompt = "Binary file"

    try:
        message = generate_commit_message(diff_for_prompt, config.model)  # Use config.model
        # print_commit_message(message, 0, 1, terminal_width, args.test) # Removed

        # The patch content is simply the full diff we received for whole-file processing
        # For deleted files, the patch is generated by get_diff.
        # For binary files, staging happens via git add, so patch content is not strictly needed for apply. Mark it?
        # Let's store the full diff patch content here. If it's binary/deleted, _apply_commits handles it differently.
        patch_content_for_commit = (
            full_diff_patch if not file.get("is_binary", False) else None
        )  # Use None for binary

        # Return data instead of committing
        return {
            "group_index": 1,  # Only one group for whole file
            "total_groups": 1,
            "hunk_indices": [],  # Not applicable for whole file
            "message": message,
            "patch_content": patch_content_for_commit,  # Store the patch
            "num_hunks_in_group": 1,  # Treat whole file as one 'hunk' conceptually
            "total_hunks_in_file": 1,
            # Add status and is_binary flags to help _apply_commits
            "status": status,
            "is_binary": file.get("is_binary", False),
        }

    except OpenAIError:
        # Error already logged by ai module
        # Still return structure indicating failure if possible
        return {
            "group_index": 1,
            "total_groups": 1,
            "hunk_indices": [],
            "message": "[Chore] Commit changes (AI Error)",
            "patch_content": None,
            "num_hunks_in_group": 1,
            "total_hunks_in_file": 1,
            "status": status,
            "is_binary": file.get("is_binary", False),
            "error": "AI Error",
        }
    except Exception as e:  # Catch other unexpected errors
        console.print(f"Unexpected error processing file {path}: {e}", style="warning")
        return {
            "group_index": 1,
            "total_groups": 1,
            "hunk_indices": [],
            "message": "[Chore] Commit changes (System Error)",
            "patch_content": None,
            "num_hunks_in_group": 1,
            "total_hunks_in_file": 1,
            "status": status,
            "is_binary": file.get("is_binary", False),
            "error": "System Error",
        }

    # --- Commit Logic (Deferred) ---
    """
    staged_successfully = False
    # Stage the file...
    # Commit the file...
    """


def _process_files_parallel(
    files: list[dict[str, Any]],
    config: Config,
    repo: GitRepository,  # <-- Add repo argument
) -> list[list[dict[str, Any]] | None]:  # Replaced individual args with config
    # ... existing code ...

    def process_file_wrapper(file, file_index):
        """Wrapper to process a file and put results in the queue."""
        # Process hunks/file and get the structured commit data, passing config and repo
        commit_data = _process_file_hunks(file, config, repo)  # Returns list or None
        # Put the result (list of groups or None) along with the original index into the queue
        # result_queue.put((file_index, commit_data)) # Old logic, results stored directly now

    # Determine max workers based on parallel setting
    if config.parallel <= 0:  # Use config.parallel
        # Auto mode: Use CPU count * 2 but limit based on files
        max_workers = min(len(files), os.cpu_count() * 2)
    else:
        # Use specified level but ensure we don't exceed files
        max_workers = min(len(files), config.parallel)  # Use config.parallel

    threads = []
    active_threads = []  # Keep track of active threads
    file_queue = list(enumerate(files))  # Create a queue of files to process

    lock = threading.Lock()
    results = [(None)] * len(files)  # Pre-allocate results list

    def worker():
        """Pulls files from queue and processes them."""
        while True:
            with lock:
                if not file_queue:
                    return  # No more files
                index, file = file_queue.pop(0)

            try:
                # Pass repo to the wrapper
                commit_data = _process_file_hunks(file, config, repo)
                with lock:
                    results[index] = commit_data  # Store result by original index
            except Exception as e:
                # Log error and store None to indicate failure for this file
                console.print(
                    f"Error processing file {file.get('path', 'unknown')} in thread: {e}",
                    style="warning",
                )
                with lock:
                    results[index] = None

    # Start worker threads
    for _ in range(max_workers):
        thread = threading.Thread(target=worker)
        thread.start()
        active_threads.append(thread)

    # Wait for all threads to complete
    for thread in active_threads:
        thread.join()

    # Results are already in order in the `results` list
    processed_data: list[list[dict[str, Any]] | None] = results
    return processed_data

    # --- Old threading logic (removed) ---
    # Start a thread for each file (controlled parallelism)
    # threads = []
    # for i, file in enumerate(files):
    #     thread = threading.Thread(target=process_file_wrapper, args=(file, i))
    #     threads.append(thread)
    #     thread.start()
    #
    #     # Limit concurrent threads to max_workers
    #     if len(threads) >= max_workers:
    #         threads[0].join()
    #         threads.pop(0)
    #
    # # Wait for all threads to complete
    # for thread in threads:
    #     thread.join()
    #
    # # Collect results in original file order
    # results = []
    # while not result_queue.empty():
    #     results.append(result_queue.get())
    #
    # # Sort by original index
    # results.sort(key=lambda x: x[0])
    #
    # # Return the collected commit data list, ordered by original file index
    # # Ensure the return type matches the signature
    # processed_data: list[list[dict[str, Any]] | None] = [r[1] for r in results]
    # return processed_data


def _build_commit_tree(
    repo: GitRepository,  # Add repo argument
    files_commit_data: list[list[dict[str, Any]] | None],
    files: list[dict[str, Any]],
) -> tuple[Tree, dict[tuple[int, int], Panel], dict[int, str], int, int]:
    """
    Builds the rich Tree visualization for the commit plan.

    Args:
        repo: The GitRepository instance.
        files_commit_data: Processed commit data for each file.
        files: Original list of changed files.

    Returns:
        A tuple containing:
        - The constructed Tree object.
        - A dictionary mapping (file_index, group_index) to the Panel to update with hash.
        - A dictionary mapping file index to the chosen commit message (first group's).
        - The count of processed files added to the tree.
        - The total number of commit messages generated (potential commits).
    """
    # --- Header Panel & Width Calculation ---
    repo_name = repo.get_repository_name()
    term_width = console.width
    # Panel width will be ~3/4 of terminal width, used for alignment and message box
    panel_width = int(term_width * 0.75)
    header_width = min(term_width - 4, 60)  # Keep header width potentially smaller
    title_text = Text.assemble(
        (GIT_ICON + "  ", "preview_header_title"), (repo_name, "preview_header_title")
    )
    # Pad title text to fill width, right-align search icon (removed search icon for this header)
    padding_needed = header_width - len(title_text) - 2  # -2 for panel borders
    padded_title = Text.assemble(
        title_text,
        (" " * max(0, padding_needed), "default"),
    )
    # Manually construct the header text to match the desired style
    top_border = f"╭{'─' * header_width}╮"
    bottom_border = f"╰{'─' * header_width}╯"
    # Ensure title fits within the width, accounting for border characters '│ │'
    title_line_content = Text.assemble(
        ("│ ", "preview_header_border"),
        padded_title,  # Already calculated with padding
        (" │", "preview_header_border"),
    )
    # Combine header lines into a single Text object for the tree label
    tree_header_text = Text.assemble(
        (top_border, "preview_header_border"),
        "\n",
        title_line_content,
        "\n",
        (bottom_border, "preview_header_border"),
    )

    # --- Tree ---
    tree = Tree(
        tree_header_text,  # Use the manually constructed text as the tree label/header
        guide_style="blue",
    )

    total_commits_generated = 0
    processed_files_count = 0
    commit_panels_to_update: dict[tuple[int, int], Panel] = {}  # Map (file_idx, group_idx) -> Panel
    file_commit_messages: dict[int, str] = {}

    for file_index, commit_groups in enumerate(files_commit_data):
        if commit_groups is None:
            continue

        original_file_info = files[file_index]
        path = original_file_info["path"]
        plus, minus = original_file_info["plus_minus"]
        status = original_file_info["status"]

        # --- File Node Label (Right-aligned stats) ---
        file_icon_text = Text(FILE_ICON + " ", style="file_header")
        path_text = Text(path, style="file_path")
        stats_text = Text.assemble(
            (f" {plus}", "file_stats_plus"), ("  ", "default"), (f" {minus}", "file_stats_minus")
        )
        # Calculate padding needed for right alignment against the panel width
        # Target width accounts for tree indentation (~4) and panel width
        target_width = panel_width + 4
        current_len = len(file_icon_text) + len(path_text)
        padding_needed = target_width - current_len - len(stats_text)
        padding = " " * max(0, padding_needed)
        file_label = Text.assemble(file_icon_text, path_text, padding, stats_text)

        file_node = tree.add(file_label)
        processed_files_count += 1

        total_hunks_in_file = commit_groups[0].get("total_hunks_in_file", 0) if commit_groups else 0
        if total_hunks_in_file > 1:
            file_node.add(f" [hunk_info]Found {total_hunks_in_file} Hunks[/]")

        if commit_groups:
            file_commit_messages[file_index] = commit_groups[0]["message"]

        for group_index, group_data in enumerate(commit_groups):
            if "message generation failed" not in group_data["message"]:
                total_commits_generated += 1
            num_hunks_in_group = group_data.get("num_hunks_in_group", "?")

            # --- Group Node Label (Right-aligned stats) ---
            group_icon_text = Text(" ", style="group_header")
            group_name_text = Text(
                f"Group {group_data['group_index']} / {group_data['total_groups']}",
                style="group_header",
            )
            group_stats_text = Text(f" {num_hunks_in_group}", style="hunk_info")
            # Calculate padding for right alignment against the panel width
            # Target width accounts for tree indentation (~8 for group level) and panel width
            group_target_width = panel_width + 8
            group_current_len = len(group_icon_text) + len(group_name_text)
            group_padding_needed = group_target_width - group_current_len - len(group_stats_text)
            group_padding = " " * max(0, group_padding_needed)
            group_label = Text.assemble(
                group_icon_text, group_name_text, group_padding, group_stats_text
            )

            group_node = file_node.add(group_label)

            # --- Commit Panel ---
            # Remove hash placeholder
            panel_title_text = "Message "
            # Calculate title padding
            # Panel width will be ~3/4 of terminal width
            panel_width = int(term_width * 0.75)
            title_padding_len = (
                panel_width - len(" ") - len(panel_title_text) - 4
            )  # Account for borders/padding
            title_padding = "─" * max(0, title_padding_len)  # Use line char for padding

            panel_title = Text.assemble(
                (" ", "commit_title"),
                (title_padding, "commit_panel_border"),  # Use border style for padding
                (" ", "default"),
                (panel_title_text, "commit_title"),
            )

            # Format commit message with indented word-wrapping
            commit_text_content = group_data["message"]
            indent = "      "  # 6 spaces for body indentation
            # Calculate available width inside the panel (panel_width - borders/padding)
            wrap_width = panel_width - 4
            lines = commit_text_content.splitlines()
            title = lines[0] if lines else ""
            body_lines = lines[1:] if len(lines) > 1 else []

            wrapped_body = []
            for line in body_lines:
                # Preserve leading whitespace (like hyphens) before wrapping
                leading_whitespace = ""
                stripped_line = line
                if line.startswith(("- ", "* ")):  # Common list markers
                    leading_whitespace = line[
                        : line.find(line.lstrip())
                    ]  # Capture original indent/marker
                    stripped_line = line.lstrip()

                # Wrap the stripped line content
                wrapped_lines = textwrap.wrap(
                    stripped_line,
                    width=wrap_width
                    - len(indent)
                    - len(leading_whitespace),  # Adjust width for indents
                    initial_indent="",
                    subsequent_indent=indent
                    + leading_whitespace,  # Apply full indent on subsequent lines
                    replace_whitespace=False,
                    drop_whitespace=False,
                )
                # Add the main indent and original leading whitespace to the first wrapped line
                if wrapped_lines:
                    wrapped_body.append(indent + leading_whitespace + wrapped_lines[0])
                    wrapped_body.extend(
                        wrapped_lines[1:]
                    )  # Subsequent lines already have indent from textwrap

            # Join title and formatted body
            formatted_content = title
            if wrapped_body:
                # Add a blank line between title and body if body exists
                formatted_content += "\n\n" + "\n".join(wrapped_body)

            commit_text = Text(formatted_content, style="commit_message")
            # No need for pad_left anymore

            commit_panel = Panel(
                commit_text,
                title=panel_title,
                title_align="left",
                border_style="commit_panel_border",
                box=ROUNDED,
                width=panel_width,  # Set width
                expand=False,  # Prevent expanding beyond width
            )
            group_node.add(commit_panel)
            # Store panel keyed by (file_index, group_index - 1 for 0-based access)
            commit_panels_to_update[(file_index, group_data["group_index"] - 1)] = (
                commit_panel  # Use 0-based index
            )

    return (
        tree,
        commit_panels_to_update,
        file_commit_messages,
        processed_files_count,
        total_commits_generated,
    )


# Removed old _apply_commits function


def process_files(
    repo: GitRepository, files: list[dict[str, Any]], config: Config
) -> tuple[int, int, int, int]:  # Added repo argument
    """
    Process files, generate commit messages, display them in a tree,
    optionally commit/push, and return summary counts.

    Args:
        repo: An initialized GitRepository object.
        files: List of files to process.
        config: The application configuration object.

    Returns:
        Tuple of (processed_files_count, total_commits_made, total_lines_changed, total_files)
    """
    # Removed internal repo instantiation, it's now injected

    total_files = len(files)
    total_lines_changed = sum(
        f["plus_minus"][0] + f["plus_minus"][1] for f in files if f and "plus_minus" in f
    )
    # terminal_width = get_terminal_width() # No longer needed here

    # Print test banner if active
    if config.test_mode is not None:
        # Manually print the banner with exact characters
        console.print("╭◉ ", style="test_mode")
        console.print("│", style="test_mode")
        console.print("│             TEST MODE: ON", style="test_mode")
        console.print("│       CHANGES ARE ONLY VISUAL ", style="test_mode")
        console.print("│", style="test_mode")
        console.print("╰◉", style="test_mode")
        console.print()  # Add a blank line after banner

    # --- Render Repository Preview ---
    # Get changed files info (already available in 'files' list)
    render_repository_preview(
        repo_name=repo.get_repository_name(),
        repo_path=repo.path,
        changed_files=files,  # Pass the list of changed files
    )
    # The function already prints a newline after the tree

    # --- 1. Data Collection (Parallel) ---
    console.print("Analyzing changes and generating messages/patches...", style="info") # Updated message

    # Apply test limit if needed
    files_to_process = files
    if config.test_mode is not None:  # Use config.test_mode
        # Ensure test value is at least 1 if provided as 0 or negative
        max_files = max(1, config.test_mode)  # Use config.test_mode
        files_to_process = files[:max_files]
        console.print(f"Test Mode: Processing only the first {len(files_to_process)} file(s).", style="test_mode")

    # This now returns a list where each item corresponds to a file and contains
    # a list of its commit groups (dictionaries) or None if processing failed.
    # Pass the potentially sliced list to the parallel processor, including repo
    files_commit_data = _process_files_parallel(files_to_process, config, repo)  # Pass config and repo
    console.print("Message generation complete.", style="success")

    # --- 2. Tree Construction ---
    (
        tree,
        commit_panels_to_update,
        file_commit_messages,
        processed_files_count,
        total_commits_generated,
    ) = _build_commit_tree(repo, files_commit_data, files)  # Pass repo

    # --- 3. Print Tree ---
    console.print("\n" * 2)  # Add spacing
    console.print(tree)
    console.print("\n" * 1)  # Add spacing

    # --- 4. Commit Logic ---
    total_commits_made = 0
    committed_files_list = []  # Initialize list for committed files
    if config.test_mode is None:  # Use config.test_mode
        total_commits_made, committed_files_list = _apply_commits(  # Capture committed files list
            repo,
            files_commit_data,
            files,
            # file_commit_messages, # Removed
            commit_panels_to_update,  # Pass updated dict
            tree,
        )
    elif config.test_mode is not None:
        console.print(f"Test Mode: Skipping {total_commits_generated} potential commits.", style="test_mode")
        # In test mode, show all files that would have been processed as 'committed'
        committed_files_list = [f["path"] for f_idx, f_groups in enumerate(files_commit_data) if f_groups is not None for f in files if files[f_idx]["path"] == f["path"] ]

    # --- 5. Push (Optional) ---
    push_status = "not_attempted"  # Default status
    if config.push and total_commits_made > 0 and config.test_mode is None:
        try:
            target_branch = config.branch or repo.get_current_branch()
            console.print(f"\nPushing to {config.remote}/{target_branch}...", style="push_info")
            repo.push(config.remote, target_branch)
            console.print("Push successful.", style="success")
            push_status = "pushed"
        except GitRepositoryError as e:
            console.print(f"Push operation failed: {e}", style="warning")
            push_status = "failed"
        except Exception as e:
            console.print(f"An unexpected error occurred during push setup: {e}", style="warning")
            push_status = "failed"
    elif config.push and total_commits_made > 0 and config.test_mode is not None:
        console.print("Test Mode: Would push.", style="test_mode")
        push_status = "skipped"  # Skipped due to test mode
    elif config.push and total_commits_made == 0:
        # console.print("\nSkipping push: No commits were made.", style="info") # Optional message
        push_status = "skipped"  # Skipped because no commits

    # --- 6. Final Summary ---
    # Import the function if not already done (should be at top)
    from autocommit.utils.console import render_final_summary

    render_final_summary(
        repo_name=repo.get_repository_name(),
        repo_path=repo.path,
        committed_files=committed_files_list,  # Pass the list from _apply_commits
        push_status=push_status,  # Pass the determined status
    )

    # Return the calculated counts
    return processed_files_count, total_commits_made, total_lines_changed, total_files
