#!/usr/bin/env python3
"""
Main processing module for AutoCommit.
"""

import argparse
import concurrent.futures
import os
from queue import Queue
import threading
from typing import Any, Dict, List, Tuple, Optional

from rich.tree import Tree
from rich.panel import Panel
from rich.box import ROUNDED
from rich.text import Text
from rich.align import Align

from autocommit.core.ai import classify_hunks, generate_commit_message
from autocommit.core.diff import split_diff_into_chunks
from autocommit.utils.console import (
    console,
    get_terminal_width,
    # Remove old print functions, will add new helpers later if needed
    # print_commit_message,
    # print_file_info,
)
from autocommit.utils.git import run_git_command


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
            except Exception as e:
                console.print(
                    f"Error generating message for chunk {chunk_index}: {e}", style="warning"
                )
                messages[chunk_index] = "[Chore] Commit changes"

    return messages


def _process_file_hunks(
    file: dict[str, Any], args: argparse.Namespace, terminal_width: int
) -> Optional[List[Dict[str, Any]]]:
    """
    Process hunks for a single file, group them, and generate messages.

    Args:
        file: File information including path, diff, and status.
        args: Command-line arguments.
        terminal_width: Terminal width (may not be needed here anymore).

    Returns:
        List of dictionaries, each representing a commit group with its message,
        or None if processing fails or no hunks are found.
    """
    path = file["path"]
    diff = file["diff"]
    status = file["status"] # Keep status for potential commit logic later

    # console.print(f"Processing file: {path}", style="info") # Debug print

    # Skip binary files or deleted files - handle them with _process_whole_file
    if diff in {"Binary file", "File was deleted"}:
        result = _process_whole_file(file, args, terminal_width)
        return [result] if result else None # Wrap single result in list

    # Split the diff into hunks
    hunks = split_diff_into_chunks(diff, args.chunk_level)

    if not hunks:
        # console.print(f"No hunks found for {path}", style="warning") # Less verbose now
        return None

    # If there's only one hunk, process the whole file
    if len(hunks) == 1:
        result = _process_whole_file(file, args, terminal_width)
        return [result] if result else None # Wrap single result in list

    # console.print(f"Found {len(hunks)} hunks in {path}", style="info") # Less verbose

    # Classify hunks into logically related groups
    try:
        hunk_groups = classify_hunks(hunks, args.model)
    except Exception as e:
        console.print(f"Error classifying hunks for {path}: {e}", style="warning")
        # Fallback: treat all hunks as one group
        hunk_groups = [hunks]

    if args.debug:
        console.print(f"DEBUG: Classified {len(hunks)} hunks into {len(hunk_groups)} groups for {path}", style="debug")
    # console.print(f"Grouped into {len(hunk_groups)} logical groups", style="info") # Less verbose

    # Since we can't easily stage individual hunks, we'll use a simpler approach:
    # We'll just process the whole file for each group and generate separate commit messages

    commit_data_list = []

    # Generate messages for each group
    for i, group in enumerate(hunk_groups, 1):
        # console.print(f"\nProcessing hunk group {i}/{len(hunk_groups)} for {path}", style="info") # Less verbose

        # Combine the diffs from all hunks in this group
        group_diff = "\n".join(hunk["diff"] for hunk in group)
        group_hunk_indices = [hunk.get("original_index", -1) for hunk in group] # Assuming split_diff adds original_index

        # Generate a commit message for this group
        try:
            message = generate_commit_message(group_diff, args.model)
        except Exception as e:
            console.print(f"Error generating message for group {i} in {path}: {e}", style="warning")
            message = "[Chore] Commit changes (message generation failed)"

        commit_data_list.append({
            "group_index": i,
            "total_groups": len(hunk_groups),
            "hunk_indices": group_hunk_indices, # Track which original hunks are in this group
            "message": message,
            "diff": group_diff, # Keep diff for potential later commit logic
            "num_hunks_in_group": len(group),
            "total_hunks_in_file": len(hunks)
        })

    return commit_data_list

    # --- Commit Logic (Deferred) ---
    # The actual staging and committing logic needs to be moved out of here
    # and likely happen *after* the tree is displayed, using the collected data.
    # We'll keep the old logic commented out for reference for now.
    """
    total_commits = 0
    # For test mode... (removed)

    # For real mode... (removed)
    """


def _process_whole_file(
    file: dict[str, Any], args: argparse.Namespace, terminal_width: int
) -> Optional[Dict[str, Any]]:
    """
    Process a single file as a whole and generate its commit message data.

    Args:
        file: File information including path, diff, and status.
        args: Command-line arguments.
        terminal_width: Terminal width (may not be needed here).

    Returns:
        A dictionary containing the commit data (message, diff, etc.),
        or None if processing fails.
    """
    path = file["path"]
    diff = file["diff"]
    status = file["status"]

    try:
        message = generate_commit_message(diff, args.model)
        # print_commit_message(message, 0, 1, terminal_width, args.test) # Removed

        # Return data instead of committing
        return {
            "group_index": 1, # Only one group for whole file
            "total_groups": 1,
            "hunk_indices": [], # Not applicable for whole file
            "message": message,
            "diff": diff,
            "num_hunks_in_group": 1, # Treat whole file as one 'hunk' conceptually
            "total_hunks_in_file": 1
        }

    except Exception as e:
        console.print(f"Error processing file {path}: {e}", style="warning")
        return None

    # --- Commit Logic (Deferred) ---
    """
    staged_successfully = False
    # Stage the file...
    # Commit the file...
    """


def _process_files_parallel(
    files: list[dict[str, Any]], args: argparse.Namespace
) -> List[Optional[Dict[str, Any]]]:
    """
    Process multiple files in parallel to generate commit message data.

    Args:
        files: List of files to process.
        args: Command-line arguments.

    Returns:
        List containing commit data dictionaries for each file (or None if failed).
        The outer list corresponds to the input `files` list order.
        Each inner dictionary represents a file and contains a list of its commit groups.
    """
    result_queue = Queue()

    def process_file_wrapper(file, file_index):
        """Wrapper to process a file and put results in the queue."""
        terminal_width = get_terminal_width() # May not be needed now
        # Process hunks/file and get the structured commit data
        commit_data = _process_file_hunks(file, args, terminal_width) # Returns list or None
        # Put the result (list of groups or None) along with the original index into the queue
        result_queue.put((file_index, commit_data))

    # Determine max workers based on parallel setting
    if args.parallel <= 0:
        # Auto mode: Use CPU count * 2 but limit based on files
        max_workers = min(len(files), os.cpu_count() * 2)
    else:
        # Use specified level but ensure we don't exceed files
        max_workers = min(len(files), args.parallel)

    # Start a thread for each file (controlled parallelism)
    threads = []
    for i, file in enumerate(files):
        thread = threading.Thread(target=process_file_wrapper, args=(file, i))
        threads.append(thread)
        thread.start()

        # Limit concurrent threads to max_workers
        if len(threads) >= max_workers:
            threads[0].join()
            threads.pop(0)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect results in original file order
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    # Sort by original index
    results.sort(key=lambda x: x[0])

    # Return the collected commit data list, ordered by original file index
    return [r[1] for r in results] # r[1] is the commit_data (list or None)


def process_files(
    files: list[dict[str, Any]], args: argparse.Namespace
) -> tuple[int, int, int, int]: # Restore original return type
    """
    Process files, generate commit messages, display them in a tree,
    optionally commit/push, and return summary counts.

    Args:
        files: List of files to process.
        args: Command-line arguments.

    Returns:
        Tuple of (processed_files_count, total_commits_made, total_lines_changed, total_files)
    """
    total_files = len(files)
    total_lines_changed = sum(f["plus_minus"][0] + f["plus_minus"][1] for f in files if f and "plus_minus" in f) # Added check for None/missing key
    terminal_width = get_terminal_width() # Keep for potential panel width calculation

    # --- 1. Data Collection (Parallel) ---
    console.print("Analyzing changes and generating messages...", style="info")

    # Apply test limit if needed
    files_to_process = files
    if args.test is not None:
        # Ensure test value is at least 1 if provided as 0 or negative
        max_files = max(1, args.test)
        console.print(f"Test Mode: Limiting processing to {max_files} file(s).", style="test_mode")
        files_to_process = files[:max_files]

    # This now returns a list where each item corresponds to a file and contains
    # a list of its commit groups (dictionaries) or None if processing failed.
    # Pass the potentially sliced list to the parallel processor
    files_commit_data = _process_files_parallel(files_to_process, args)
    console.print("Message generation complete.", style="success")

    # --- 2. Tree Construction ---
    # Match the target style more closely
    tree = Tree(
        f"╭────────────────────╮\n│   [bold yellow] AutoCommit[/]     │\n╰────────────────────╯",
        guide_style="blue", # Use a simpler guide style
        # highlight=True # Enable highlighting for markdown/styles within nodes if needed
    )

    total_commits_generated = 0
    processed_files_count = 0

    for file_index, commit_groups in enumerate(files_commit_data):
        if commit_groups is None:
            # Handle case where processing failed for a file (already logged in worker)
            continue

        original_file_info = files[file_index]
        path = original_file_info["path"]
        plus, minus = original_file_info["plus_minus"]
        status = original_file_info["status"] # Needed for commit logic later

        # Add file node to the tree with right-aligned stats
        file_stats = Text.assemble(
            (" ", "default"), # Spacer
            (f" {plus}", "file_stats_plus"),
            ("  ", "default"),
            (f" {minus}", "file_stats_minus"),
            (" ", "default") # Spacer
        )
        # Use Align.right for stats, but need total width. Let's try manual padding first.
        # Calculate padding needed (this is tricky without knowing exact widths)
        # For now, just append stats, alignment needs more work if this isn't good enough.
        file_label = Text.assemble(
            (" ", "file_header"),
            (path, "file_path"), # Use specific style for path
            (f"   ", "default"), # Spacer
            (f" {plus}", "file_stats_plus"),
            ("  ", "default"),
            (f" {minus}", "file_stats_minus")
        )
        file_node = tree.add(file_label)
        processed_files_count += 1

        total_hunks_in_file = commit_groups[0].get("total_hunks_in_file", 0) if commit_groups else 0
        if total_hunks_in_file > 1: # Only show hunk count if > 1
            file_node.add(f" [hunk_info]Found {total_hunks_in_file} Hunks[/]")

        for group_data in commit_groups:
            total_commits_generated += 1
            num_hunks_in_group = group_data.get('num_hunks_in_group', '?')
            group_label = Text.assemble(
                (" ", "group_header"),
                (f"Group {group_data['group_index']} / {group_data['total_groups']}", "group_header"),
                (f"   ", "default"), # Spacer
                (f" {num_hunks_in_group}", "hunk_info") # Hunk count for the group
            )
            group_node = file_node.add(group_label)

            # Add individual hunks (optional, maybe too verbose?)
            # for hunk_idx in group_data.get("hunk_indices", []):
            #     group_node.add(f"  Hunk {hunk_idx + 1}") # Assuming 0-based index needs +1

            # Create commit message panel with refined title and border
            # Placeholder for actual hash - needs to be retrieved after commit
            commit_hash_placeholder = "{SHORT_HASH}"
            panel_title = Text.assemble(
                (" ", "commit_title"),
                (commit_hash_placeholder, "commit_hash"),
                (" ────────────── ", "commit_panel_border"), # Match example line
                ("Message ", "commit_title")
            )
            # Add padding to the left of the commit message text
            commit_text = Text.assemble(("   ", "default"), (group_data['message'], "commit_message"))
            commit_panel = Panel(
                commit_text, # Use padded text
                title=panel_title,
                title_align="left",
                border_style="commit_panel_border", # Use theme style
                box=ROUNDED, # Keep rounded box
                expand=True # Let panel expand
            )
            group_node.add(commit_panel)

    # --- 3. Print Tree ---
    console.print("\n" * 2) # Add spacing
    console.print(tree)
    console.print("\n" * 1) # Add spacing

    # --- 4. Commit Logic (Placeholder/Deferred) ---
    # The actual committing needs to happen here, iterating through
    # files_commit_data and using the stored diffs/messages.
    # This needs careful handling of staging based on groups/hunks.
    total_commits_made = 0
    if not args.test:
        console.print("Applying commits (placeholder)...", style="info")
        # Placeholder: In a real implementation, iterate through files_commit_data
        # and perform git add/commit operations based on the groups.
        # For now, just simulate based on generated messages.
        total_commits_made = total_commits_generated # Simulate success for now
        console.print(f"Simulated {total_commits_made} potential commits (based on generated groups).", style="success")
    else:
        limit_msg = f" (limited to {max(1, args.test)} file(s))" if args.test is not None else ""
        console.print(f"Test Mode: Would generate {total_commits_generated} commit messages{limit_msg}.", style="test_mode")
        total_commits_made = total_commits_generated # In test mode, count generated ones

    # --- Push (Optional) ---
    # --- 5. Push (Optional) ---
    if args.push and total_commits_made > 0:
        # from autocommit.utils.console import print_push_info # Need to refactor this too
        from autocommit.core.commit import push_commits

        console.print(f"Pushing to {args.remote}/{args.branch}...", style="push_info")
        # print_push_info(args.remote, args.branch, terminal_width) # Refactor needed
        if not args.test:
            push_commits(args.remote, args.branch, args.test) # Assumes push_commits handles errors
        else:
            console.print("Test Mode: Would push.", style="test_mode")

    # --- 6. Final Summary (Optional) ---
    # console.print(f"\nSummary: Processed {processed_files_count}/{total_files} files, "
    #               f"Made {total_commits_made} commits.", style="summary_header")

    # Return the calculated counts
    return processed_files_count, total_commits_made, total_lines_changed, total_files
