#!/usr/bin/env python3
"""
Console output utilities.
"""

from pathlib import Path
from typing import Any, Literal

from rich.console import Console
from rich.text import Text
from rich.theme import Theme
from rich.tree import Tree

# --- Layout Constants ---
DOTS_END_COLUMN = 50  # Fixed column position where dots should end

# --- Icons ---
# File System Icons
FOLDER_ICON = " "
FOLDER_OPEN_ICON = " "
FOLDER_EMPTY_ICON = " "
FILE_ICON = " "
PYTHON_ICON = " "
MARKDOWN_ICON = "󰂺 "
JSON_ICON = " "
YAML_ICON = " "
TEXT_ICON = " "
IMAGE_ICON = " "
ARCHIVE_ICON = " "
SHELL_ICON = " "
HTML_ICON = " "
CSS_ICON = " "
JAVASCRIPT_ICON = " "
TYPESCRIPT_ICON = " "  # Often used alongside JS
C_ICON = " "
CPP_ICON = " "  # C++
JAVA_ICON = " "
RUST_ICON = " "
GO_ICON = " "
DOCKERFILE_ICON = "󰡨 "
CONFIG_ICON = " "  # Generic config like .ini, .toml
LOCK_ICON = " "  # e.g., package-lock.json, poetry.lock
PDF_ICON = " "
DATABASE_ICON = " "
WORD_ICON = " "
EXCEL_ICON = " "
POWERPOINT_ICON = " "
AUDIO_ICON = " "
VIDEO_ICON = " "
CODE_ICON = " "
BAK_ICON = " "

# Git Specific Icons
GIT_ICON = ""
BRANCH_ICON = ""
TAG_ICON = ""
STATUS_MODIFIED_ICON = " "
STATUS_ADDED_ICON = " "
STATUS_DELETED_ICON = " "
STATUS_RENAMED_ICON = " "
STATUS_UNTRACKED_ICON = ""

# General UI Icons
SEARCH_ICON = ""
CLOCK_ICON = " "
GEAR_ICON = " "

# Status/Feedback Icons
STATUS_OK_ICON = " "  # 
WARNING_ICON = " "  # 
ERROR_ICON = " "
INFO_ICON = " "

# Map git status codes to icons (simplified)
STATUS_ICONS = {
    "M": STATUS_MODIFIED_ICON,
    "A": STATUS_ADDED_ICON,
    "D": STATUS_DELETED_ICON,
    "R": STATUS_RENAMED_ICON,
    "C": STATUS_MODIFIED_ICON,
    "U": STATUS_MODIFIED_ICON,
    "??": STATUS_UNTRACKED_ICON,
}

# Setup Rich console with custom theme (adjust as needed for new style)
custom_theme = Theme({
    "file_header": "bold yellow",
    "file_path": "dim yellow",
    "file_stats_plus": "green",
    "file_stats_minus": "red",
    "hunk_info": "dim cyan",
    "group_header": "bold bright_blue",
    "commit_panel_border": "blue",
    "commit_title": "bold green",
    "commit_hash": "dim green",
    "commit_message": "white",
    "push_info": "magenta",
    "summary_header": "bold cyan",
    "summary_item": "cyan",
    "warning": "bold red",
    "success": "bold green",
    "test_mode": "bold yellow",
    "info": "dim cyan",
    "debug": "dim magenta",
    "preview_dir": "default",
    "preview_file": "default",
    "preview_dots": "dim blue",
    "preview_status_ok": "green",
    "preview_status_changed": "yellow",
    "preview_header_border": "blue",
    "preview_header_title": "bold",
})
console = Console(theme=custom_theme, highlight=False)


def _add_path_to_tree(
    path: Path,
    tree_node: Tree,
    repo_root: Path,
    changed_files_set: set[str],
    changed_files_map: dict[str, str],
    indentation_level: int = 0,  # Track indentation level for alignment
):
    """Recursively adds directory contents to the Rich Tree for preview."""
    # Define padding/spacing constants
    icon_space = 2  # e.g., " "

    try:
        # Sort items by type (dirs first) then name
        items = sorted(list(path.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        console.print(
            f" [dim]Skipping inaccessible directory: {path.relative_to(repo_root)}[/]",
            style="warning",
        )
        return
    except Exception as e:
        console.print(
            f" [dim]Error reading directory {path.relative_to(repo_root)}: {e}[/]", style="warning"
        )
        return

    for item in items:
        # Skip hidden files/dirs and __pycache__
        if item.name.startswith(".") or item.name == "__pycache__":
            continue

        relative_path_str = str(item.relative_to(repo_root)).replace("\\", "/")
        display_name = item.name

        # Calculate the current position based on indentation level and name length
        # Tree indentation is typically 4 spaces per level
        tree_indent = 4 * (indentation_level + 1)  # +1 because root node already has indentation
        current_position = tree_indent + icon_space + len(display_name)

        # Calculate dots needed to reach the fixed DOTS_END_COLUMN
        dots_needed = max(0, DOTS_END_COLUMN - current_position)
        dots = "." * dots_needed

        if item.is_dir():
            # Always add directories
            node_label = Text.assemble(
                (FOLDER_ICON + " ", "preview_dir"),
                (display_name, "preview_dir"),
                (dots, "preview_dots"),
                (STATUS_OK_ICON, "preview_status_ok"),
            )
            child_node = tree_node.add(node_label)
            # Pass indentation_level + 1 down recursively
            _add_path_to_tree(
                item,
                child_node,
                repo_root,
                changed_files_set,
                changed_files_map,
                indentation_level + 1,
            )
        elif item.is_file():
            # Only add files if they are changed
            if relative_path_str in changed_files_set:
                status_code = changed_files_map.get(relative_path_str, "??")  # Get status
                status_icon = STATUS_ICONS.get(
                    status_code[0], STATUS_UNTRACKED_ICON
                )  # Use first char for status map

                # Choose file icon based on extension (simple example)
                file_icon = FILE_ICON
                if item.suffix == ".py":
                    file_icon = PYTHON_ICON
                elif item.suffix == ".md":
                    file_icon = MARKDOWN_ICON

                # Recalculate dots for files as icon might differ
                file_current_position = tree_indent + icon_space + len(display_name)
                file_dots_needed = max(0, DOTS_END_COLUMN - file_current_position)
                file_dots = "." * file_dots_needed

                node_label = Text.assemble(
                    (file_icon + " ", "preview_file"),
                    (display_name, "preview_file"),
                    (file_dots, "preview_dots"),
                    (status_icon, "preview_status_changed"),  # Use specific style for changed files
                )
                tree_node.add(node_label)


def render_repository_preview(
    repo_name: str,
    repo_path: str,
    changed_files: list[dict[str, Any]],
):
    """Renders a tree view of the repository changes."""
    term_width = console.width
    header_width = min(term_width - 4, 60)
    title_text = Text.assemble(
        (GIT_ICON + "  ", "preview_header_title"), ("Repository Preview", "preview_header_title")
    )
    padding_needed = header_width - len(title_text) - 2
    padded_title = Text.assemble(title_text, (" " * max(0, padding_needed), "default"))
    top_border = f"╭{'─' * header_width}╮"
    bottom_border = f"╰{'─' * header_width}╯"
    title_line = Text.assemble(
        ("│ ", "preview_header_border"),
        padded_title,
        (" │", "preview_header_border"),
    )

    console.print(top_border, style="preview_header_border")
    console.print(title_line)
    console.print(bottom_border, style="preview_header_border")

    tree = Tree(f"└── {FOLDER_ICON}  ./ ({repo_path})", guide_style="blue")

    # Store directory nodes to avoid duplicates and ensure structure
    dir_nodes: dict[str, Tree] = {".": tree}

    for file_data in changed_files:
        path_str = file_data["path"]
        parts = Path(path_str).parts
        current_path = Path(".")
        parent_node = tree

        # Create directory nodes
        for i, part in enumerate(parts[:-1]):
            current_path = current_path / part
            path_key = str(current_path)
            if path_key not in dir_nodes:
                # Find parent node based on parent path
                parent_path_key = str(current_path.parent)
                parent_node = dir_nodes.get(
                    parent_path_key, tree
                )  # Default to root if parent not found
                dir_nodes[path_key] = parent_node.add(f"{FOLDER_ICON}  {part}", guide_style="blue")
            # Update parent_node for the next level
            parent_node = dir_nodes[path_key]

        # Add file node
        file_name = parts[-1]
        plus, minus = file_data["plus_minus"]
        status = file_data["status"]

        # Status decoration (optional, can be adapted)
        status_color = {
            "M": "yellow",
            "A": "green",
            "D": "red",
            "R": "blue",
            "C": "cyan",
            "??": "magenta",
        }.get(status.strip(), "white")
        status_text = Text(f"[{status.strip()}]", style=status_color)

        file_icon_text = Text(FILE_ICON + "  ", style="file_header")
        path_text = Text(file_name, style="file_path")
        stats_text = Text.assemble(
            (f" +{plus}", "file_stats_plus"), (" ", "default"), (f"-{minus}", "file_stats_minus")
        )

        # Basic alignment - combine elements
        # More complex alignment might be needed depending on desired look
        file_label = Text.assemble(file_icon_text, path_text, " ", stats_text, " ", status_text)

        # Add file to the correct parent node
        parent_path_key = str(Path(path_str).parent)
        parent_node = dir_nodes.get(parent_path_key, tree)  # Default to root
        parent_node.add(file_label)

    console.print(tree)
    console.print()  # Add a blank line after the tree


def get_terminal_width() -> int:
    """Get terminal width."""
    # Removed try-except, console.width handles it
    return console.width


def render_final_summary(
    repo_name: str,
    repo_path: str,
    committed_files: list[str],
    push_status: Literal["pushed", "failed", "skipped", "not_attempted"],
):
    """Renders the final summary after commits and optional push."""
    term_width = console.width
    header_width = min(term_width - 4, 60)
    title_text = Text.assemble(
        (GIT_ICON + "  ", "preview_header_title"),
        ("Commit Summary", "preview_header_title"),  # Changed title
    )
    padding_needed = header_width - len(title_text) - 2
    padded_title = Text.assemble(title_text, (" " * max(0, padding_needed), "default"))
    top_border = f"╭{'─' * header_width}╮"
    bottom_border = f"╰{'─' * header_width}╯"
    title_line = Text.assemble(
        ("│ ", "preview_header_border"),
        padded_title,
        (" │", "preview_header_border"),
    )

    console.print(top_border, style="preview_header_border")
    console.print(title_line)
    console.print(bottom_border, style="preview_header_border")

    if not committed_files:
        console.print("No files were committed in this run.", style="info")
    else:
        tree = Tree(f"└── {FOLDER_ICON}  ./", guide_style="dim blue")  # Simpler root
        dir_nodes: dict[str, Tree] = {".": tree}

        # Sort files for consistent tree structure
        committed_files.sort()

        for path_str in committed_files:
            try:
                parts = Path(path_str).parts
                current_path_str = "."
                parent_node = tree

                # Create directory nodes
                for i, part in enumerate(parts[:-1]):
                    # Build the path key incrementally
                    current_path_key = str(Path(current_path_str) / part)
                    if current_path_key not in dir_nodes:
                        # Find parent node based on parent path string
                        parent_path_key = str(Path(current_path_str))
                        parent_node = dir_nodes.get(
                            parent_path_key, tree
                        )  # Default to root if parent not found
                        # Add new directory node
                        dir_nodes[current_path_key] = parent_node.add(
                            f"{FOLDER_ICON}  {part}", guide_style="dim blue"
                        )
                    # Update parent_node and current_path_str for the next level
                    parent_node = dir_nodes[current_path_key]
                    current_path_str = current_path_key  # Update the string path

                # Add file node
                file_name = parts[-1]
                file_icon_text = Text(FILE_ICON + "  ", style="file_header")
                path_text = Text(file_name, style="file_path")
                success_icon = Text(f"  {STATUS_OK_ICON}", style="success")  # Added space

                # Basic alignment
                file_label = Text.assemble(file_icon_text, path_text, success_icon)

                # Add file to the correct parent node
                parent_path_key = str(Path(path_str).parent)
                parent_node = dir_nodes.get(parent_path_key, tree)  # Default to root
                parent_node.add(file_label)
            except Exception as e:
                # Log error if path parsing/tree building fails for a file
                console.print(
                    f"Error adding file to summary tree '{path_str}': {e}", style="warning"
                )

        console.print(tree)

    # --- Push Status ---
    console.print("\n--- Push Status ---", style="bold")
    if push_status == "pushed":
        console.print(f"{STATUS_OK_ICON} Changes pushed successfully.", style="success")
    elif push_status == "failed":
        console.print(f"{ERROR_ICON} Push failed. Check logs above.", style="error")
    elif push_status == "skipped":
        console.print(f"{INFO_ICON} Push skipped (Test Mode or no commits).", style="info")
    elif push_status == "not_attempted":
        console.print(f"{INFO_ICON} Push not requested.", style="info")

    console.print("\n")  # Final newline
