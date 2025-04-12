#!/usr/bin/env python3
"""
Main processing module for AutoCommit.
"""

# import argparse -> No longer used
import concurrent.futures
import os
from queue import Queue
import threading
from typing import Any, Dict, List, Tuple, Optional

from autocommit.core.config import Config # Import Config

from rich.tree import Tree
from rich.panel import Panel
from rich.box import ROUNDED
from rich.text import Text
from rich.align import Align

from autocommit.core.ai import classify_hunks, generate_commit_message, OpenAIError # Import OpenAIError
from autocommit.core.diff import split_diff_into_chunks
from autocommit.core.git_repository import GitRepository, GitRepositoryError # Added GitRepository
from autocommit.utils.console import (
    console,
    # get_terminal_width, -> No longer used
    # Old print functions removed
)
# from autocommit.utils.git import run_git_command # No longer needed directly here


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
            except OpenAIError as e: # Catch specific error
                # Error already logged by ai module
                messages[chunk_index] = "[Chore] Commit changes (AI Error)"
            except Exception as e: # Catch other unexpected errors
                console.print(
                    f"Unexpected error generating message for chunk {chunk_index}: {e}", style="warning"
                )
                messages[chunk_index] = "[Chore] Commit changes (System Error)"

    return messages


def _process_file_hunks(
    file: dict[str, Any], config: Config
) -> Optional[List[Dict[str, Any]]]: # Replaced individual args with config
    """
    Process hunks for a single file, group them, and generate messages.

    Args:
        file: File information including path, diff, and status.
        config: The application configuration object.

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
        # Pass specific args instead of the whole namespace
        result = _process_whole_file(file, config) # Pass config
        return [result] if result else None

    # Split the diff into hunks
    hunks = split_diff_into_chunks(diff, config.chunk_level) # Use config.chunk_level

    if not hunks:
        # console.print(f"No hunks found for {path}", style="warning") # Less verbose now
        return None

    # If there's only one hunk, process the whole file
    if len(hunks) == 1:
        # Pass specific args instead of the whole namespace
        result = _process_whole_file(file, config) # Pass config
        return [result] if result else None

    # console.print(f"Found {len(hunks)} hunks in {path}", style="info") # Less verbose

    # Classify hunks into logically related groups
    try:
        hunk_groups = classify_hunks(hunks, config.model, config.debug) # Pass debug flag
    except OpenAIError as e:
        # Error already logged by ai module
        console.print(f"Classification failed for {path}, treating as single group.", style="warning")
        hunk_groups = [hunks] # Fallback
    except Exception as e: # Catch other unexpected errors
        console.print(f"Unexpected error during hunk classification for {path}: {e}", style="warning")
        hunk_groups = [hunks] # Fallback

    if config.debug: # Use config.debug
        console.print(f"[debug]DEBUG:[/] Classified {len(hunks)} hunks into {len(hunk_groups)} groups for [file_path]{path}[/]", style="debug")
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
            message = generate_commit_message(group_diff, config.model) # Use config.model
        except OpenAIError as e:
             # Error already logged by ai module
             message = "[Chore] Commit changes (AI Error)"
        except Exception as e: # Catch other unexpected errors
             console.print(f"Unexpected error generating message for group {i} in {path}: {e}", style="warning")
             message = "[Chore] Commit changes (System Error)"

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
    file: dict[str, Any], config: Config
) -> Optional[Dict[str, Any]]: # Replaced model with config
    """
    Process a single file as a whole and generate its commit message data.

    Args:
        file: File information including path, diff, and status.
        config: The application configuration object.

    Returns:
        A dictionary containing the commit data (message, diff, etc.),
        or None if processing fails.
    """
    path = file["path"]
    diff = file["diff"]
    status = file["status"]

    try:
        message = generate_commit_message(diff, config.model) # Use config.model
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

    except OpenAIError:
        # Error already logged by ai module
        return None # Indicate failure
    except Exception as e: # Catch other unexpected errors
        console.print(f"Unexpected error processing file {path}: {e}", style="warning")
        return None

    # --- Commit Logic (Deferred) ---
    """
    staged_successfully = False
    # Stage the file...
    # Commit the file...
    """


def _process_files_parallel(
    files: list[dict[str, Any]], config: Config
) -> List[Optional[List[Dict[str, Any]]]]: # Replaced individual args with config
    """
    Process multiple files in parallel to generate commit message data.

    Args:
        files: List of files to process.
        config: The application configuration object.

    Returns:
        List containing commit data dictionaries for each file (or None if failed).
        The outer list corresponds to the input `files` list order.
        Each item in the outer list is a list of commit group dictionaries for that file, or None if processing failed.
    """
    result_queue = Queue()

    def process_file_wrapper(file, file_index):
        """Wrapper to process a file and put results in the queue."""
        # Process hunks/file and get the structured commit data, passing config
        commit_data = _process_file_hunks(file, config) # Returns list or None
        # Put the result (list of groups or None) along with the original index into the queue
        result_queue.put((file_index, commit_data))

    # Determine max workers based on parallel setting
    if config.parallel <= 0: # Use config.parallel
        # Auto mode: Use CPU count * 2 but limit based on files
        max_workers = min(len(files), os.cpu_count() * 2)
    else:
        # Use specified level but ensure we don't exceed files
        max_workers = min(len(files), config.parallel) # Use config.parallel

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
    # Ensure the return type matches the signature
    processed_data: List[Optional[List[Dict[str, Any]]]] = [r[1] for r in results]
    return processed_data


def _build_commit_tree(
    files_commit_data: List[Optional[List[Dict[str, Any]]]],
    files: List[Dict[str, Any]]
) -> Tuple[Tree, Dict[Tuple[int, int], Panel], Dict[int, str], int, int]: # Changed panel dict type
    """
    Builds the rich Tree visualization for the commit plan.

    Returns:
        A tuple containing:
        - The constructed Tree object.
        - A dictionary mapping (file_index, group_index) to the Panel to update with hash.
        - A dictionary mapping file index to the chosen commit message (first group's).
        - The count of processed files added to the tree.
        - The total number of commit messages generated (potential commits).
    """
    tree = Tree(
        f"╭────────────────────╮\n│   [bold yellow] AutoCommit[/]     │\n╰────────────────────╯",
        guide_style="blue",
    )

    total_commits_generated = 0
    processed_files_count = 0
    commit_panels_to_update: Dict[Tuple[int, int], Panel] = {} # Map (file_idx, group_idx) -> Panel
    file_commit_messages: Dict[int, str] = {}

    for file_index, commit_groups in enumerate(files_commit_data):
        if commit_groups is None:
            continue

        original_file_info = files[file_index]
        path = original_file_info["path"]
        plus, minus = original_file_info["plus_minus"]
        status = original_file_info["status"]
        # No need to initialize list per file anymore

        file_label = Text.assemble(
            (" ", "file_header"),
            (path, "file_path"),
            (f"   ", "default"),
            (f" {plus}", "file_stats_plus"),
            ("  ", "default"),
            (f" {minus}", "file_stats_minus")
        )
        file_node = tree.add(file_label)
        processed_files_count += 1

        total_hunks_in_file = commit_groups[0].get("total_hunks_in_file", 0) if commit_groups else 0
        if total_hunks_in_file > 1:
            file_node.add(f" [hunk_info]Found {total_hunks_in_file} Hunks[/]")

        if commit_groups:
            file_commit_messages[file_index] = commit_groups[0]['message']

        for group_index, group_data in enumerate(commit_groups):
            if "message generation failed" not in group_data['message']:
                 total_commits_generated += 1
            num_hunks_in_group = group_data.get('num_hunks_in_group', '?')
            group_label = Text.assemble(
                (" ", "group_header"),
                (f"Group {group_data['group_index']} / {group_data['total_groups']}", "group_header"),
                (f"   ", "default"),
                (f" {num_hunks_in_group}", "hunk_info")
            )
            group_node = file_node.add(group_label)

            commit_hash_placeholder = "{SHORT_HASH}"
            panel_title = Text.assemble(
                (" ", "commit_title"),
                (commit_hash_placeholder, "commit_hash"),
                (" ────────────── ", "commit_panel_border"),
                ("Message ", "commit_title")
            )
            commit_text = Text.assemble(("   ", "default"), (group_data['message'], "commit_message"))
            commit_panel = Panel(
                commit_text,
                title=panel_title,
                title_align="left",
                border_style="commit_panel_border",
                box=ROUNDED,
                expand=True
            )
            group_node.add(commit_panel)
            # Store panel keyed by (file_index, group_index)
            commit_panels_to_update[(file_index, group_index)] = commit_panel

    return tree, commit_panels_to_update, file_commit_messages, processed_files_count, total_commits_generated

def _apply_commits(
    repo: GitRepository,
    files_commit_data: List[Optional[List[Dict[str, Any]]]],
    files: List[Dict[str, Any]],
    commit_panels_to_update: Dict[Tuple[int, int], Panel], # Key is (file_idx, group_idx)
    tree: Tree
) -> int: # Removed file_commit_messages param
    """
    Applies the actual commits based on the generated messages.

    Returns:
        The number of commits successfully made.
    """
    total_commits_made = 0
    console.print("\nApplying commits...", style="info")
    for file_index, commit_groups in enumerate(files_commit_data):
        if commit_groups is None:
            continue # Skip files that failed processing

        original_file_info = files[file_index]
        path = original_file_info["path"]
        console.print(f"\nProcessing commits for [file_path]{path}[/]...", style="info")

        # Track if any commit succeeded for this file to avoid redundant staging warnings
        commit_succeeded_for_file = False

        for group_index, group_data in enumerate(commit_groups):
            group_message = group_data.get("message")
            # Use group_data['group_index'] which is 1-based from generation
            panel_key = (file_index, group_data['group_index'] - 1) # Adjust to 0-based index for list access
            panel_to_update = commit_panels_to_update.get(panel_key)

            if not group_message or "message generation failed" in group_message or "AI Error" in group_message or "System Error" in group_message:
                console.print(f"  Skipping Group {group_data['group_index']} (invalid message: '{group_message[:30]}...').", style="warning")
                if panel_to_update:
                     panel_to_update.title = Text.assemble(
                         (" ", "warning"), ("Skipped (Invalid Msg)", "warning"), (" ─── ", "commit_panel_border"), ("Message ", "commit_title")
                     )
                continue

            commit_hash = None
            try:
                # Stage the *entire file* before each group commit attempt
                # Only print staging message once per file if first attempt or previous failed
                if group_index == 0 or not commit_succeeded_for_file:
                     console.print(f"  Staging {path}...", style="info")
                repo.stage_files([path]) # Raises GitRepositoryError on failure

                console.print(f"  Attempting commit for Group {group_data['group_index']}...", style="info")
                commit_hash = repo.commit(group_message) # Commit with the group's message

            except GitRepositoryError as e:
                console.print(f"  Error processing commit for Group {group_data['group_index']}: {e}", style="warning")
                if panel_to_update:
                     panel_to_update.title = Text.assemble(
                         (" ", "warning"), ("Commit Failed", "warning"), (" ───────── ", "commit_panel_border"), ("Message ", "commit_title")
                     )
                # Don't continue to next group for this file if staging/commit failed fundamentally
                break # Exit inner loop for this file

            if commit_hash and commit_hash != "Success (hash unavailable)":
                total_commits_made += 1
                commit_succeeded_for_file = True # Mark success for this file
                console.print(f"  Committed Group {group_data['group_index']} as [commit_hash]{commit_hash}[/]", style="success")
                if panel_to_update:
                     new_title = Text.assemble(
                         (" ", "commit_title"), (commit_hash, "commit_hash"), (" ────────────── ", "commit_panel_border"), ("Message ", "commit_title")
                     )
                     panel_to_update.title = new_title
            elif commit_hash == "Success (hash unavailable)":
                 total_commits_made += 1
                 commit_succeeded_for_file = True
                 console.print(f"  Committed Group {group_data['group_index']} (hash unavailable)", style="success")
                 if panel_to_update:
                      new_title = Text.assemble(
                          (" ", "commit_title"), ("{HASH N/A}", "commit_hash"), (" ──────────── ", "commit_panel_border"), ("Message ", "commit_title")
                      )
                      panel_to_update.title = new_title
            else:
                # Nothing to commit (changes likely included in a previous group's commit for this file)
                # Only print skip message if a previous commit for this file succeeded
                if commit_succeeded_for_file:
                     console.print(f"  Skipped Group {group_data['group_index']} (no changes left to commit for this file).", style="info")
                     if panel_to_update:
                          panel_to_update.title = Text.assemble(
                              (" ", "info"), ("Already Committed", "info"), (" ─── ", "commit_panel_border"), ("Message ", "commit_title")
                          )
                else:
                     # This case might happen if the first group commit fails silently (e.g., empty commit)
                     console.print(f"  Skipped Group {group_data['group_index']} (no changes detected).", style="info")
                     if panel_to_update:
                          panel_to_update.title = Text.assemble(
                              (" ", "warning"), ("Skipped (No Changes)", "warning"), (" ── ", "commit_panel_border"), ("Message ", "commit_title")
                          )

    # Re-print the tree if commits were made to show updated hashes
    if total_commits_made > 0:
         console.print("\nCommit tree updated with hashes:")
         console.print(tree)
         console.print("\n")

    return total_commits_made

def process_files(repo: GitRepository, files: list[dict[str, Any]], config: Config) -> tuple[int, int, int, int]: # Added repo argument
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
    total_lines_changed = sum(f["plus_minus"][0] + f["plus_minus"][1] for f in files if f and "plus_minus" in f)
    # terminal_width = get_terminal_width() # No longer needed here

    # Print test banner if active
    if config.test_mode is not None:
        banner_text = (
            "╭◉ \n"
            "│\n"
            "│       TEST MODE: ON\n"
            "│   CHANGES ARE ONLY VISUAL\n"
            "│\n"
            "╰◉"
        )
        console.print(banner_text, style="test_mode")
        console.print()  # Add a blank line after banner

    # --- 1. Data Collection (Parallel) ---
    console.print("Analyzing changes and generating messages...", style="info")

    # Apply test limit if needed
    files_to_process = files
    if config.test_mode is not None: # Use config.test_mode
        # Ensure test value is at least 1 if provided as 0 or negative
        max_files = max(1, config.test_mode) # Use config.test_mode
        console.print(f"Test Mode: Limiting processing to {max_files} file(s).", style="test_mode")
        files_to_process = files[:max_files]

    # This now returns a list where each item corresponds to a file and contains
    # a list of its commit groups (dictionaries) or None if processing failed.
    # Pass the potentially sliced list to the parallel processor
    files_commit_data = _process_files_parallel(files_to_process, config) # Pass config
    console.print("Message generation complete.", style="success")

    # --- 2. Tree Construction ---
    (tree,
     commit_panels_to_update,
     file_commit_messages,
     processed_files_count,
     total_commits_generated) = _build_commit_tree(files_commit_data, files)

    # --- 3. Print Tree ---
    console.print("\n" * 2) # Add spacing
    console.print(tree)
    console.print("\n" * 1) # Add spacing

    # --- 4. Commit Logic ---
    total_commits_made = 0
    if config.test_mode is None: # Use config.test_mode
        total_commits_made = _apply_commits(
            repo,
            files_commit_data,
            files,
            # file_commit_messages, # Removed
            commit_panels_to_update, # Pass updated dict
            tree
        )

    else: # In test mode
        # Test mode summary
        limit_msg = f" (limited to {max(1, config.test_mode)} file(s))" if config.test_mode is not None else ""
        console.print(f"\nTest Mode: Would attempt {total_commits_generated} commit(s){limit_msg} based on generated messages.", style="test_mode")
        # In test mode, 'made' commits is 0, but we report potential ones
        # total_commits_made = 0 # Already initialized

    # --- Push (Optional) ---
    # --- 5. Push (Optional) ---
    if config.push and total_commits_made > 0: # Use config.push
        # from autocommit.utils.console import print_push_info # Need to refactor this too
        # Use the GitRepository instance for pushing
        # Determine target branch (respecting args.branch or getting current)
        try:
            target_branch = config.branch or repo.get_current_branch() # Raises GitRepositoryError
            console.print(f"\nPushing to {config.remote}/{target_branch}...", style="push_info")
            if config.test_mode is None:
                 repo.push(config.remote, target_branch) # Raises GitRepositoryError
                 console.print("Push successful.", style="success")
            else:
                console.print("Test Mode: Would push.", style="test_mode")
        except GitRepositoryError as e:
             # Error already logged if it came from get_current_branch or push
             console.print(f"Push operation failed: {e}", style="warning")
        except Exception as e: # Catch other unexpected errors
             console.print(f"An unexpected error occurred during push setup: {e}", style="warning")

    # --- 6. Final Summary (Optional) ---
    # console.print(f"\nSummary: Processed {processed_files_count}/{total_files} files, "
    #               f"Made {total_commits_made} commits.", style="summary_header")

    # Return the calculated counts
    return processed_files_count, total_commits_made, total_lines_changed, total_files
