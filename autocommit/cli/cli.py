#!/usr/bin/env python3
"""
Command-line interface for AutoCommit.
"""

import argparse
import os

from autocommit.core.diff import split_diff_into_chunks
from autocommit.core.files import get_uncommitted_files
from autocommit.core.processor import process_files
from autocommit.utils.console import console


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
        help="Control commit atomicity: 0=coarse (file level), 1=standard (default), "
        "2=fine (logical units), 3=atomic (single responsibility)",
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
    parser = create_parser()
    args = parser.parse_args()

    # Check if we're in a git repository
    if not os.path.exists(".git"):
        console.print("Error: Not in a git repository", style="warning")
        return 1

    # Get uncommitted files
    files = get_uncommitted_files(args)
    if not files:
        console.print("No uncommitted changes found", style="warning")
        return 0

    # Process the files
    processed_files, total_commits, total_lines, total_files = process_files(files, args)

    # Print summary
    console.print("\nSummary: ", style="summary_header")
    console.print(f"\t- {processed_files}/{total_files} files tracked", style="summary_item")
    # Update for the different chunk levels
    total_chunks = sum(
        len(split_diff_into_chunks(f["diff"], args.chunk_level))
        for f in files
        if not f["is_binary"]
    )
    console.print(f"\t- {total_commits}/{total_chunks} changes committed", style="summary_item")
    console.print(f"\t- {processed_files}/{total_files} files uploaded", style="summary_item")
    console.print(f"\t- {total_lines} lines of code changed", style="summary_item")
    chunk_levels = ["file-level", "standard", "logical units", "atomic"]
    console.print(
        f"\t- Chunk level: {args.chunk_level} ({chunk_levels[args.chunk_level]})",
        style="summary_item",
    )

    # Display parallelism information
    parallel_mode = "auto" if args.parallel <= 0 else str(args.parallel)
    console.print(f"\t- Parallelism: {parallel_mode}", style="summary_item")

    # Display test mode message if active
    if args.test:
        console.print("\nTESTING MODE WAS ON. NO CHANGES WERE MADE.", style="test_mode")

    return 0
