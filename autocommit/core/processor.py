#!/usr/bin/env python3
"""
Main processing module for AutoCommit.
"""

import argparse
import concurrent.futures
import os
from queue import Queue
import threading
from typing import Any

from autocommit.core.ai import generate_commit_message
from autocommit.utils.console import (
    console,
    get_terminal_width,
    print_commit_message,
    print_file_info,
)


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


def _process_file(
    file: dict[str, Any], args: argparse.Namespace, terminal_width: int
) -> tuple[str, str, str] | None:
    """
    Process a single file: generate a commit message based on its diff.
    Returns a tuple (file_path, commit_message, file_status) or None if message generation fails.
    """
    path = file["path"]
    diff = file["diff"]
    status = file["status"]

    print_file_info(file, terminal_width)

    try:
        # Generate one commit message for the entire file's diff
        # Note: We could enhance this later to combine chunk messages if needed.
        message = generate_commit_message(diff, args.model)
        print_commit_message(message, 0, 1, terminal_width, args.test) # Display the generated message

        # Return info needed for bulk staging/commit
        return (path, message, status)
    except Exception as e:
        console.print(f"Error generating message for {path}: {e}", style="warning")
        # Optionally return a default message or None to skip
        # For now, let's return a default message to ensure the file is still committed
        default_message = f"chore: Update {os.path.basename(path)}"
        print_commit_message(default_message, 0, 1, terminal_width, args.test, is_default=True)
        return (path, default_message, status)


def _process_files_parallel(
    files: list[dict[str, Any]], args: argparse.Namespace
) -> list[tuple[str, str, str]]:
    """
    Process multiple files in parallel to generate commit messages.
    Returns a list of tuples: (file_path, commit_message, file_status).
    """
    result_queue = Queue()
    # No lock needed here as we are just collecting results, not modifying shared state

    def process_file_wrapper(file, file_index):
        """Wrapper to process a file and put results in the queue."""
        terminal_width = get_terminal_width()
        result = _process_file(file, args, terminal_width) # Returns (path, message, status) or None

        # Put the result along with the original index into the queue
        result_queue.put((file_index, result))

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

    # Filter out None results (errors during message generation) and return path, message, status
    # Keep the original order based on file_index
    return [r[1] for r in results if r[1] is not None]

# The following return statement was orphaned from the previous edit and needs removal.

def process_files(
    files: list[dict[str, Any]], args: argparse.Namespace
) -> tuple[int, int, int, int]:
    """Process files, generate commit messages, and create commits."""
    total_files = len(files)
    total_lines_changed = sum(f["plus_minus"][0] + f["plus_minus"][1] for f in files)
    terminal_width = get_terminal_width()

    console.print("\nFiles to Process and Commit:", style="summary_header")
    for file in files:
        path = file["path"]
        plus, minus = file["plus_minus"]
        # Format the path and plus/minus counts
        path_display = path
        plus_minus_display = f"+{plus} / -{minus}"

        # Print the file header
        dots_count = terminal_width - len(path_display) - len(plus_minus_display) - 4
        dots = "·" * dots_count

        console.print(f"    {path_display} {dots} {plus_minus_display}", style="file_header")

    console.print("\n\nResults:", style="summary_header")

    # Process files in parallel but commit each file's changes sequentially
    results = _process_files_parallel(files, args)

    # --- Generate Messages ---
    # results is now a list of tuples: (file_path, commit_message, file_status)
    results = _process_files_parallel(files, args)

    if not results:
        console.print("No files processed or messages generated.", style="warning")
        return 0, 0, total_lines_changed, total_files # No commits made

    # Import necessary functions here to avoid potential circular dependencies
    from autocommit.utils.git import run_git_command
    from autocommit.core.commit import push_commits

    def print_warnings(warnings):
        """Helper to print formatted warnings."""
        for warning in warnings:
            if warning["type"] == "LineEndingLFtoCRLF":
                console.print(
                    f"    [yellow]Line Ending Conversion:[/] [bold yellow]LF[/] → [bold green]CRLF[/] in '{warning['file']}'",
                    style="dim" # Use dim style for less intrusive warnings
                )
            # Add other warning types here
            else:
                 console.print(f"    [yellow]Git Warning:[/] {warning['type']} - {warning['file']}", style="dim")

    # --- Stage and Commit Individually ---
    total_commits = 0
    processed_files_count = 0 # Track successfully processed files for commit

    for file_path, commit_message, status in results:
        staged_successfully = False
        committed_successfully = False

        console.print(f"\nProcessing commit for: [file_path]{file_path}[/]", style="info")

        # --- Stage Individual File ---
        if status.startswith("D"): # Deleted file
            rm_result = run_git_command(["git", "rm", file_path])
            if rm_result["warnings"]:
                print_warnings(rm_result["warnings"])
            if rm_result["error"]:
                console.print(f"Error staging deleted file {file_path}: {rm_result['error']}", style="error")
            else:
                staged_successfully = True
        else: # Added or Modified file
            add_result = run_git_command(["git", "add", file_path])
            if add_result["warnings"]:
                print_warnings(add_result["warnings"])
            if add_result["error"]:
                console.print(f"Error staging file {file_path}: {add_result['error']}", style="error")
            else:
                staged_successfully = True

        # --- Commit Individual File ---
        if staged_successfully:
            if args.test:
                console.print(f"  [bold cyan]Test Mode: Would commit '{file_path}' with message:[/]")
                console.print(f"  ```\n  {commit_message}\n  ```")
                committed_successfully = True # Simulate success in test mode
            else:
                commit_result = run_git_command(["git", "commit", "-m", commit_message])
                if commit_result["warnings"]:
                    print_warnings(commit_result["warnings"])

                commit_stderr = commit_result["stderr"]
                if "nothing to commit" in commit_stderr:
                    console.print(f"  Nothing to commit for {file_path} (already committed or no changes staged?).", style="info")
                    # Don't count this as a successful commit for this run
                elif commit_result["error"]:
                    console.print(f"  Error committing {file_path}: {commit_result['error']}", style="error")
                    # Consider attempting 'git reset HEAD <file_path>'? Maybe too complex/risky.
                else:
                    console.print(f"  Successfully committed {file_path}.", style="success")
                    committed_successfully = True

        if committed_successfully:
            total_commits += 1
            processed_files_count += 1 # Count files that were successfully committed
        else:
            console.print(f"  Skipping commit for {file_path} due to staging or commit error.", style="warning")


    # --- Push (Optional) ---
    if args.push and total_commits > 0:
        from autocommit.utils.console import print_push_info  # Import here
        print_push_info(args.remote, args.branch, terminal_width)
        if not args.test:
            push_commits(args.remote, args.branch, args.test)


    # Return counts using the count of successfully committed files
    # total_commits now reflects the number of individual commits made
    return processed_files_count, total_commits, total_lines_changed, total_files
