#!/usr/bin/env python3
"""
Command-line interface for AutoCommit.
"""

import argparse
import os

# Import Console class directly, keep custom_theme
from rich.console import Console
from autocommit.core.diff import split_diff_into_chunks
from autocommit.core.files import get_uncommitted_files
from autocommit.core.processor import process_files
# Remove import of the shared console object
# from autocommit.utils.console import console
from autocommit.utils.console import custom_theme


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="AutoCommit: AI-powered Git commit message generator"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test mode, don't actually commit changes"
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

    # Get uncommitted files
    files = get_uncommitted_files(args) # This function might use the shared console internally
    if not files:
        # Need to decide if get_uncommitted_files should use shared or local console
        # For now, assume it might print warnings using the shared one from utils
        # If it fails, we might need to pass a console object to it.
        # Let's use the local one here for consistency for now.
        local_console_init.print("No uncommitted changes found", style="warning")
        return 0

    # Process the files - This function now prints the main tree using the shared console from utils
    processed_files, total_commits, total_lines, total_files = process_files(files, args)

    # --- Summary Printing ---
    # Create a NEW Console instance specifically for the summary, applying the theme
    summary_console = Console(theme=custom_theme, highlight=False)

    # Print summary using the dedicated summary_console
    summary_console.print("\nSummary: ", style="summary_header")
    summary_console.print(f"\t- {processed_files}/{total_files} files tracked", style="summary_item")
    # Update for the different chunk levels
    total_chunks = sum(
        len(split_diff_into_chunks(f["diff"], args.chunk_level))
        for f in files
        if f and "diff" in f and not f.get("is_binary", False) # Added checks for safety
    )
    summary_console.print(f"\t- {total_commits}/{total_chunks} changes committed", style="summary_item")
    # summary_console.print(f"\t- {processed_files}/{total_files} files uploaded", style="summary_item") # This line might be misleading
    summary_console.print(f"\t- {total_lines} lines of code changed", style="summary_item")
    chunk_levels = ["file-level", "standard", "logical units", "atomic"]
    summary_console.print(
        f"\t- Chunk level: {args.chunk_level} ({chunk_levels[args.chunk_level]})",
        style="summary_item",
    )

    # Display parallelism information
    parallel_mode = "auto" if args.parallel <= 0 else str(args.parallel)
    summary_console.print(f"\t- Parallelism: {parallel_mode}", style="summary_item")

    # Display test mode message if active
    if args.test:
        summary_console.print("\nTESTING MODE WAS ON. NO CHANGES WERE MADE.", style="test_mode")

    return 0
