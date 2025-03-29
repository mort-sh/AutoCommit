#!/usr/bin/env python3
"""
Console output utilities.
"""

import shutil
import textwrap
from typing import Any

from rich.console import Console
from rich.theme import Theme

from autocommit.core.constants import INDENT_LEVEL_2, INDENT_LEVEL_3, INDENT_LEVEL_4

# Setup Rich console with custom theme
custom_theme = Theme({
    "file_header": "bold yellow",
    "commit_header": "bold green",
    "commit_message": "blue",
    "push_info": "magenta",
    "summary_header": "bold cyan",
    "summary_item": "cyan",
    "warning": "bold red",
    "success": "bold green",
    "test_mode": "bold yellow",
})
console = Console(theme=custom_theme)


def print_file_info(file: dict[str, Any], width: int) -> None:
    """Print information about a file."""
    path = file["path"]
    plus, minus = file["plus_minus"]

    # Format the path and plus/minus counts
    path_display = textwrap.shorten(path, width=width - 20, placeholder="...")
    plus_minus_display = f"+{plus} / -{minus}"

    # Print the file header
    dots_count = width - len(path_display) - len(plus_minus_display) - 4
    dots = "·" * dots_count

    console.print(f"    {path_display} {dots} {plus_minus_display}", style="file_header")


def print_commit_message(
    message: str, chunk_index: int, chunks_total: int, width: int, test_mode: bool = False
) -> None:
    """Print a commit message with pretty formatting."""
    # Header for the commit message
    chunk_header = ""
    if chunks_total > 1:
        chunk_header = f"Chunk [ {chunk_index + 1} / {chunks_total} ]"

    # Calculate the displayed width of the header including tabs expanded
    header_prefix = "TEST " if test_mode else ""
    header_text = f"{INDENT_LEVEL_2}{header_prefix}Commit Message"
    expanded_header = header_text.expandtabs(8)  # Assuming tab width of 8 spaces

    # Calculate how many dots we need
    dots_count = max(0, width - len(expanded_header) - len(chunk_header) - 4)
    dots = "·" * dots_count

    console.print(
        f"{INDENT_LEVEL_2}{header_prefix}Commit Message {dots} {chunk_header}",
        style="test_mode" if test_mode else "commit_header",
    )
    console.print(f"{INDENT_LEVEL_3}{{")

    # Format and print the commit message with indentation
    for line in message.splitlines():
        console.print(f"{INDENT_LEVEL_4}{line}", style="commit_message")

    console.print(f"{INDENT_LEVEL_3}}}")
    console.print()


def print_push_info(remote: str, branch: str, width: int) -> None:
    """Print information about pushing to remote."""
    push_message = f"Pushing  @{remote}/{branch}"

    console.print(f"{INDENT_LEVEL_2}{push_message}", style="push_info")
    console.print(f"\n{INDENT_LEVEL_2}Complete\n", style="success")


def get_terminal_width() -> int:
    """Get the terminal width for formatting."""
    return shutil.get_terminal_size().columns - 10
