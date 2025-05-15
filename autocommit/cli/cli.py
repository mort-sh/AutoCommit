#!/usr/bin/env python3
"""
Command-line interface for AutoCommit.
"""

import argparse
import os

# Import Console class directly, keep custom_theme
from rich.console import Console

from autocommit.core.config import Config
from autocommit.core.diff import split_diff_into_chunks
from autocommit.core.files import get_uncommitted_files
from autocommit.core.git_repository import GitRepository, GitRepositoryError  # Import GitRepository
from autocommit.core.processor import process_files
from autocommit.utils.console import custom_theme

# from autocommit.utils.console import console # Shared console not used here


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="AutoCommit: AI-powered Git commit message generator"
    )
    parser.add_argument(
        "--test",
        nargs="?",
        type=int,
        const=1,
        default=None,  # Use None to indicate test mode is off by default
        help="Test mode: process up to N files (default 1 if flag is present without value). Automatically tracks untracked files.",
    )
    parser.add_argument("--push", action="store_true", help="Push commits after creating them")
    parser.add_argument("--remote", default="origin", help="Remote repository to push to")
    parser.add_argument("--branch", default="", help="Branch to push to (defaults to current)")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--auto-track",
        action="store_true",
        help="Automatically track all untracked files without prompting",
    )
    parser.add_argument(
        "--chunk-level",
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help="Control commit atomicity: 0=coarse (file level), 1=standard (hunk level), "
        "2=fine (logical units), 3=atomic (single responsibility). "
        "Hunks that are logically related will be grouped and committed together.",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=0,
        help="Control parallelism level: 0=auto (based on CPU cores), N=specific number of workers",
    )
    return parser


def main():
    """Main entry point for AutoCommit."""
    # Use a local console instance for initial messages if needed
    # (or import the shared one just for these, carefully)
    local_console_init = Console(theme=custom_theme)

    parser = create_parser()
    args = parser.parse_args()

    # Check if we're in a git repository
    if not os.path.exists(".git"):
        local_console_init.print("Error: Not in a git repository", style="warning")
        return 1

    # Create Config object from args
    try:
        config = Config(
            model=args.model,
            chunk_level=args.chunk_level,
            parallel=args.parallel,
            test_mode=args.test,
            push=args.push,
            remote=args.remote,
            branch=args.branch,  # Config handles empty string -> None
            debug=args.debug,
            auto_track=args.auto_track,
        )
    except ValueError as e:
        local_console_init.print(f"Configuration Error: {e}", style="warning")
        return 1

    # Instantiate GitRepository
    try:
        repo = GitRepository()
    except GitRepositoryError as e:
        local_console_init.print(f"Error initializing repository: {e}", style="warning")
        return 1

    # Get uncommitted files - Pass repo and config
    try:
        files = get_uncommitted_files(repo, config)
    except GitRepositoryError as e:
        # Handle potential errors during status/diff fetching within get_uncommitted_files
        local_console_init.print(f"Error retrieving file changes: {e}", style="warning")
        return 1
    if not files:
        local_console_init.print("No uncommitted changes found.", style="info")  # Use info style
        return 0

    # Process the files - This function now prints the main tree using the shared console from utils
    # Process the files - Pass config object
    # Process the files - Pass repo and config object
    processed_files, total_commits, total_lines, total_files = process_files(
        repo=repo, files=files, config=config
    )

    # --- Summary Printing ---
    # Create a NEW Console instance specifically for the summary, applying the theme
    summary_console = Console(theme=custom_theme, highlight=False)

    # Print summary using the dedicated summary_console
    summary_console.print("\nSummary: ", style="summary_header")
    summary_console.print(
        f"\t- {processed_files}/{total_files} files tracked", style="summary_item"
    )
    # Update for the different chunk levels
    total_chunks = sum(
        len(split_diff_into_chunks(f["diff"], config.chunk_level))  # Use config
        for f in files
        if f and "diff" in f and not f.get("is_binary", False)  # Added checks for safety
    )
    summary_console.print(
        f"\t- {total_commits}/{total_chunks} changes committed", style="summary_item"
    )
    # summary_console.print(f"\t- {processed_files}/{total_files} files uploaded", style="summary_item") # This line might be misleading
    summary_console.print(f"\t- {total_lines} lines of code changed", style="summary_item")
    chunk_levels = ["file-level", "standard", "logical units", "atomic"]
    summary_console.print(
        f"\t- Chunk level: {config.chunk_level} ({chunk_levels[config.chunk_level]})",  # Use config
        style="summary_item",
    )

    # Display parallelism information
    parallel_mode = "auto" if config.parallel <= 0 else str(config.parallel)  # Use config
    summary_console.print(f"\t- Parallelism: {parallel_mode}", style="summary_item")

    # Display test mode message if active
    if config.test_mode is not None:  # Use config
        summary_console.print("\nTESTING MODE WAS ON. NO CHANGES WERE MADE.", style="test_mode")

    return 0
