#!/usr/bin/env python3
"""
Console output utilities.
"""

from pathlib import Path
import shutil

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
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
GIT_ICON = " "
BRANCH_ICON = " "
TAG_ICON = " "
STATUS_MODIFIED_ICON = " "
STATUS_ADDED_ICON = " "
STATUS_DELETED_ICON = " "
STATUS_RENAMED_ICON = " "
STATUS_UNTRACKED_ICON = ""

# General UI Icons
SEARCH_ICON = " "
CLOCK_ICON = " "
GEAR_ICON = " "

# Status/Feedback Icons
STATUS_OK_ICON = " "  # 
WARNING_ICON = " "  # 
ERROR_ICON = " "

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


def render_repository_preview(repo_name: str, repo_path: Path, changed_files: list[dict[str, str]]):
    """Renders the repository preview tree."""
    # --- Header Panel ---
    term_width = console.width  # Use console width
    header_width = min(term_width - 4, 60)  # Max width 60, adjust for padding
    title_text = Text.assemble(
        (GIT_ICON + "  ", "preview_header_title"), (repo_name, "preview_header_title")
    )
    # Pad title text to fill width, right-align search icon
    padding_needed = (
        header_width - len(title_text) - len(SEARCH_ICON) - 2
    )  # -2 for spaces around icon
    padded_title = Text.assemble(
        title_text,
        (" " * max(0, padding_needed), "default"),  # Ensure padding isn't negative
        (SEARCH_ICON, "preview_header_title"),
    )

    # Manually construct the header to match target exactly
    top_border = f"╭{'─' * header_width}╮"
    bottom_border = f"╰{'─' * header_width}╯"
    # Ensure title fits within the width, accounting for border characters '│ │'
    title_line_content = Text.assemble(
        ("│ ", "preview_header_border"),
        title_text,
        (" " * max(0, padding_needed), "default"),  # Use calculated padding
        (SEARCH_ICON, "preview_header_title"),
        (" │", "preview_header_border"),
    )

    console.print(top_border, style="preview_header_border")
    console.print(title_line_content)  # Print the assembled Text object
    console.print(
        bottom_border, style="preview_header_border", end=""
    )  # Remove newline after header

    # --- File Tree ---
    tree = Tree(
        "",  # No root label needed for this style
        guide_style="dim blue",  # Dim guide lines
    )

    # Prepare data for quick lookup
    changed_files_set = {f["path"].replace("\\", "/") for f in changed_files}
    changed_files_map = {f["path"].replace("\\", "/"): f["status"] for f in changed_files}

    # Add root node representation manually before recursion
    root_display_name = "./"
    # Calculate dots for root node using fixed DOTS_END_COLUMN
    # Root node is at indentation level 0, with 4 spaces for the tree guide
    root_tree_indent = 4  # Tree adds this indentation for the first level
    root_icon_space = 2
    root_current_position = root_tree_indent + root_icon_space + len(root_display_name)
    root_dots_needed = max(0, DOTS_END_COLUMN - root_current_position)
    root_dots = "." * root_dots_needed

    root_label = Text.assemble(
        (FOLDER_ICON + " ", "preview_dir"),
        (root_display_name, "preview_dir"),
        (root_dots, "preview_dots"),
        (STATUS_OK_ICON, "preview_status_ok"),  # Root is always OK
    )
    root_node = tree.add(root_label)

    # Start recursion from repo root, passing indentation level 0
    _add_path_to_tree(repo_path, root_node, repo_path, changed_files_set, changed_files_map, 0)

    console.print(tree)
    console.print()  # Add spacing after the tree


def get_terminal_width() -> int:
    """Get the terminal width for formatting."""
    # Use console width directly if possible, otherwise fallback
    try:
        width = console.width
    except Exception:
        width = shutil.get_terminal_size().columns
    return width - 10  # Keep original padding logic for now


def render_final_summary(
    repo_name: str,
    repo_path: Path,
    committed_files: list[str],  # List of relative paths of committed files
    push_status: str,  # e.g., "pushed", "failed", "skipped", "not_attempted"
):
    """Renders the final summary tree and status box."""
    term_width = console.width
    header_width = min(term_width - 4, 60)  # Match other headers

    # --- Header Panel ---
    commit_header_text = Text.assemble((" ", "success"), ("Commiting Files...", "success"))
    # Pad title text to fill width, right-align icon
    commit_icon = ""
    padding_needed = header_width - len(commit_header_text) - len(commit_icon) - 2
    padded_commit_title = Text.assemble(
        commit_header_text, (" " * max(0, padding_needed), "default"), (commit_icon, "success")
    )
    commit_header_panel = Panel(
        "",  # No content inside
        title=padded_commit_title,
        title_align="left",
        border_style="green",  # Use success color
        box=ROUNDED,
        width=header_width + 2,
        height=3,
        padding=0,
    )
    console.print(commit_header_panel)

    # --- Committed Files Tree ---
    summary_tree = Tree(
        "",  # No root label needed
        guide_style="dim green",  # Use success color dimmed
    )

    # Prepare data for quick lookup
    committed_files_set = {f.replace("\\", "/") for f in committed_files}

    # Helper to add paths, modified to only show committed files/structure
    def _add_committed_to_tree(path: Path, tree_node: Tree, repo_root: Path):
        try:
            items = sorted(list(path.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
        except Exception:
            return  # Ignore errors here

        added_something = False
        for item in items:
            if item.name.startswith(".") or item.name == "__pycache__":
                continue

            relative_path_str = str(item.relative_to(repo_root)).replace("\\", "/")
            display_name = item.name
            name_width = 30
            dots = "." * max(0, name_width - len(display_name))

            if item.is_dir():
                # Check if this directory or any subdirectory contains a committed file
                contains_committed = any(
                    p.startswith(relative_path_str + "/") or p == relative_path_str
                    for p in committed_files_set
                )
                if contains_committed:
                    node_label = Text.assemble(
                        (FOLDER_ICON + " ", "preview_dir"),
                        (display_name, "preview_dir"),
                        (dots, "preview_dots"),
                        (" ", "default"),
                        (STATUS_OK_ICON, "preview_status_ok"),
                    )
                    child_node = tree_node.add(node_label)
                    if _add_committed_to_tree(item, child_node, repo_root):
                        added_something = True  # Propagate if child added something
            elif item.is_file():
                if relative_path_str in committed_files_set:
                    file_icon = FILE_ICON  # Default icon
                    if item.suffix == ".py":
                        file_icon = PYTHON_ICON
                    elif item.suffix == ".md":
                        file_icon = MARKDOWN_ICON

                    node_label = Text.assemble(
                        ("├── ", "dim default"),
                        (file_icon + " ", "preview_file"),
                        (display_name, "preview_file"),
                        (dots, "preview_dots"),
                        (" ", "default"),
                        (STATUS_OK_ICON, "preview_status_ok"),  # Committed files are OK
                    )
                    tree_node.add(node_label)
                    added_something = True
        return added_something  # Return whether this level added anything

    # Add root node representation manually
    root_display_name = "./"
    root_name_width = 30
    root_dots = "." * max(0, root_name_width - len(root_display_name))
    root_label = Text.assemble(
        (FOLDER_ICON + " ", "preview_dir"),
        (root_display_name, "preview_dir"),
        (root_dots, "preview_dots"),
        (" ", "default"),
        (STATUS_OK_ICON, "preview_status_ok"),
    )
    root_node = summary_tree.add(root_label)

    # Start recursion
    _add_committed_to_tree(repo_path, root_node, repo_path)

    console.print(summary_tree)

    # --- Status Box ---
    status_lines = []
    num_committed = len(committed_files)
    status_lines.append(
        Text.assemble(
            ("     ", "success"),
            (f"{num_committed} Files Committed", "summary_item"),
            (" ", "default"),
            ("." * (header_width - 25)),
            (" ", "default"),
            (STATUS_OK_ICON, "success"),
        )
    )

    if push_status != "not_attempted":
        push_icon = ""
        push_style = "info"
        push_end_icon = ""
        push_end_style = "success"
        push_text = "Pushing upstream"
        push_result_text = "Pushed!"

        if push_status == "failed":
            push_style = "warning"
            push_end_icon = ""
            push_end_style = "warning"
            push_result_text = "Push Failed!"
        elif push_status == "skipped":
            push_style = "dim default"
            push_end_icon = ""
            push_end_style = "dim default"
            push_text = "Push skipped"
            push_result_text = "Skipped"

        status_lines.append(
            Text.assemble(
                ("   ", "default"),
                (push_icon + "  ", push_style),
                (push_text, "summary_item"),
                (" ", "default"),
                ("." * (header_width - len(push_text) - 15)),
                (" ", "default"),
                (STATUS_OK_ICON, push_style),
            )
        )
        if push_status != "skipped":  # Only show result line if attempted
            status_lines.append(
                Text.assemble(
                    ("   ", "default"),
                    (push_icon + "  ", push_end_style),
                    (push_result_text, "summary_item"),
                    (" ", "default"),
                    ("." * (header_width - len(push_result_text) - 15)),
                    (" ", "default"),
                    (push_end_icon, push_end_style),
                )
            )

    status_content = Text("\n").join(status_lines)
    status_panel = Panel(
        status_content,
        # title="Status",
        border_style="dim default",  # Dim border for status box
        box=ROUNDED,
        width=header_width + 2,
        padding=(1, 0),  # Padding top/bottom only
        expand=False,
    )
    # Manually add connectors
    console.print("    ╭◉", style="dim default")
    console.print(status_panel)
    console.print("    ╰◉", style="dim default")
    console.print()  # Final newline
