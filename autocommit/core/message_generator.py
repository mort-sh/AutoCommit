"""
Handles the generation of commit messages, potentially in parallel.
"""

import concurrent.futures
import os

from autocommit.core.ai import OpenAIError, generate_commit_message
from autocommit.utils.console import console

# Note: _prepare_chunk_diff was previously here but seems unused
# after recent refactoring. If needed later, it can be moved back.


def generate_messages_parallel(
    diff_strings: list[str],  # List of diff strings to process
    model: str,
    # chunk_level: int, # Removed as it wasn't used internally
    parallel_level: int = 0,
) -> list[str]:
    """Generate commit messages for all provided diff strings in parallel.

    Args:
        diff_strings: A list of diff strings, each representing a chunk or group.
        model: The AI model to use for generation.
        parallel_level: The desired level of parallelism (0 for auto).

    Returns:
        A list of generated commit messages, corresponding to the input diff_strings.
        Error messages are returned in place for failed generations.
    """
    if not diff_strings:
        return []

    # Determine the number of workers based on parallel_level
    if parallel_level <= 0:
        # Auto mode: Use CPU count * 2 but limit based on number of diffs
        max_workers = min(
            len(diff_strings), (os.cpu_count() or 1) * 2
        )  # Ensure os.cpu_count() returns at least 1
    else:
        # Use specified level but ensure we don't exceed diffs
        max_workers = min(len(diff_strings), parallel_level)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create tasks for message generation using the provided diff strings directly
        future_to_index = {
            executor.submit(
                generate_commit_message,
                diff_string,
                model,  # Pass diff_string directly
            ): i
            for i, diff_string in enumerate(diff_strings)
        }

        # Collect results in order
        messages = ["[Chore] Commit changes (Generation Pending)"] * len(
            diff_strings
        )  # Initialize with placeholder
        for future in concurrent.futures.as_completed(future_to_index):
            original_index = future_to_index[future]
            try:
                messages[original_index] = future.result()
            except OpenAIError:  # Catch specific error
                # Error already logged by ai module
                messages[original_index] = "[Chore] Commit changes (AI Error)"
            except Exception as e:  # Catch other unexpected errors
                console.print(
                    f"Unexpected error generating message for diff at index {original_index}: {e}",
                    style="warning",
                )
                messages[original_index] = "[Chore] Commit changes (System Error)"

    return messages
