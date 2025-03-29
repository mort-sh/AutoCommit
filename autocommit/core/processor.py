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
from autocommit.core.commit import commit_file
from autocommit.core.diff import split_diff_into_chunks
from autocommit.utils.console import (
    console,
    get_terminal_width,
    print_commit_message,
    print_file_info,
    print_push_info,
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
) -> tuple[int, int]:
    """Process a single file - prepare chunks and generate commit messages in parallel."""
    path = file["path"]
    diff = file["diff"]
    is_binary = file["is_binary"]
    commits_made = 0

    print_file_info(file, terminal_width)

    # Handle binary files directly
    if is_binary or diff == "File was deleted":
        message = generate_commit_message(diff, args.model)
        print_commit_message(message, 0, 1, terminal_width, args.test)

        if commit_file(path, message, file["status"], args.test):
            commits_made += 1

        if args.push:
            print_push_info(args.remote, args.branch, terminal_width)
        return 1, commits_made

    # Split the diff into chunks and process each one based on chunk_level
    chunks = split_diff_into_chunks(diff, args.chunk_level)

    # Generate all commit messages in parallel
    messages = _generate_messages_parallel(chunks, args.model, args.chunk_level, args.parallel)

    # Commit each chunk sequentially (to maintain git history order)
    for i, (_, message) in enumerate(zip(chunks, messages, strict=False)):
        print_commit_message(message, i, len(chunks), terminal_width, args.test)

        # Commit the file with this message
        if commit_file(path, message, file["status"], args.test):
            commits_made += 1

    # Push after all chunks are committed
    if args.push and not args.test:
        print_push_info(args.remote, args.branch, terminal_width)

    return len(chunks), commits_made


def _process_files_parallel(
    files: list[dict[str, Any]], args: argparse.Namespace
) -> list[tuple[dict[str, Any], int, int]]:
    """Process multiple files in parallel, but commit sequentially."""
    result_queue = Queue()
    lock = threading.Lock()

    def process_file_wrapper(file, file_index):
        """Wrapper to process a file and put results in the queue."""
        terminal_width = get_terminal_width()
        chunks_processed, commits_made = _process_file(file, args, terminal_width)

        with lock:
            result_queue.put((file_index, file, chunks_processed, commits_made))

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

    # Return only the file and counts, without the index
    return [(r[1], r[2], r[3]) for r in results]


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

    # Count total processed files and commits
    processed_files = len(results)
    total_commits = sum(commits for _, _, commits in results)

    return processed_files, total_commits, total_lines_changed, total_files
