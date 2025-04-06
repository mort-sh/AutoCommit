#!/usr/bin/env python3
"""
Console output utilities.
"""

import shutil
import textwrap
from typing import Any

from rich.console import Console
from rich.panel import Panel # Keep Panel if needed for helpers later
from rich.text import Text # Keep Text if needed for helpers later
from rich.theme import Theme
from rich.tree import Tree # Keep Tree if needed for helpers later
from rich.box import ROUNDED # Keep box if needed for helpers later

# from autocommit.core.constants import INDENT_LEVEL_2, INDENT_LEVEL_3, INDENT_LEVEL_4 # No longer needed

# Setup Rich console with custom theme (adjust as needed for new style)
custom_theme = Theme({
    "file_header": "bold yellow",
    "file_path": "dim yellow", # Example style for path part
    "file_stats_plus": "green",
    "file_stats_minus": "red",
    "hunk_info": "dim cyan",
    "group_header": "bold bright_blue",
    "commit_panel_border": "blue",
    "commit_title": "bold green",
    "commit_hash": "dim green",
    "commit_message": "white", # Changed from blue
    "push_info": "magenta",
    "summary_header": "bold cyan",
    "summary_item": "cyan", # Add the missing style back
    "warning": "bold red",
    "success": "bold green",
    "test_mode": "bold yellow",
    "info": "dim cyan", # Changed from cyan
})
console = Console(theme=custom_theme, highlight=False) # highlight=False prevents Rich from messing with brackets


# Remove old print functions as the logic is now in processor.py's tree building
# def print_file_info(...) -> None: ...
# def print_commit_message(...) -> None: ...
# def print_push_info(...) -> None: ...

# We might add helper functions here later to format specific parts
# of the tree nodes or panels if the logic becomes complex in processor.py.
# For example:
# def format_file_node_label(path: str, plus: int, minus: int) -> Text: ...
# def create_commit_panel(message: str, hash_placeholder: str) -> Panel: ...


def get_terminal_width() -> int:
    """Get the terminal width for formatting."""
    return shutil.get_terminal_size().columns - 10
