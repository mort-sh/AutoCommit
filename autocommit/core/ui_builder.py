"""
Handles the construction of the Rich UI elements, primarily the commit tree.
"""
import textwrap
from typing import Any

from rich.box import ROUNDED
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from autocommit.core.git_repository import GitRepository
from autocommit.utils.console import FILE_ICON, GIT_ICON, console


def build_commit_tree(
    repo: GitRepository,
    files_commit_data: list[list[dict[str, Any]] | None],
    files: list[dict[str, Any]],
) -> tuple[Tree, dict[tuple[int, int], Panel], dict[int, str], int, int]:
    """
    Builds the rich Tree visualization for the commit plan.

    Args:
        repo: The GitRepository instance.
        files_commit_data: Processed commit data for each file.
        files: Original list of changed files information.

    Returns:
        A tuple containing:
        - The constructed Tree object.
        - A dictionary mapping (file_index, group_index-1) to the Panel to update with hash.
        - A dictionary mapping file index to the chosen commit message (first group's).
        - The count of processed files added to the tree.
        - The total number of potential commit messages generated.
    """
    # --- Header Panel & Width Calculation ---
    repo_name = repo.get_repository_name()
    term_width = console.width
    # Panel width will be ~3/4 of terminal width, used for alignment and message box
    panel_width = int(term_width * 0.75)
    header_width = min(term_width - 4, 60)  # Keep header width potentially smaller
    title_text = Text.assemble(
        (GIT_ICON + "  ", "preview_header_title"), (repo_name, "preview_header_title")
    )
    # Pad title text to fill width
    padding_needed = header_width - len(title_text) - 2  # -2 for panel borders
    padded_title = Text.assemble(
        title_text,
        (" " * max(0, padding_needed), "default"),
    )
    # Manually construct the header text to match the desired style
    top_border = f"╭{'─' * header_width}╮"
    bottom_border = f"╰{'─' * header_width}╯"
    # Ensure title fits within the width, accounting for border characters '│ │'
    title_line_content = Text.assemble(
        ("│ ", "preview_header_border"),
        padded_title,
        (" │", "preview_header_border"),
    )
    # Combine header lines into a single Text object for the tree label
    tree_header_text = Text.assemble(
        (top_border, "preview_header_border"),
        "\n",
        title_line_content,
        "\n",
        (bottom_border, "preview_header_border"),
    )

    # --- Tree ---
    tree = Tree(
        tree_header_text,
        guide_style="blue",
    )

    total_commits_generated = 0
    processed_files_count = 0
    commit_panels_to_update: dict[
        tuple[int, int], Panel
    ] = {}  # Map (file_idx, group_idx-1) -> Panel
    file_commit_messages: dict[int, str] = {}

    for file_index, commit_groups in enumerate(files_commit_data):
        if commit_groups is None:
            continue  # Skip files that failed processing

        original_file_info = files[file_index]
        path = original_file_info["path"]
        plus, minus = original_file_info["plus_minus"]
        status = original_file_info["status"]

        # --- File Node Label (Right-aligned stats) ---
        file_icon_text = Text(FILE_ICON + " ", style="file_header")
        path_text = Text(path, style="file_path")
        stats_text = Text.assemble(
            (f" {plus}", "file_stats_plus"), ("  ", "default"), (f" {minus}", "file_stats_minus")
        )
        # Calculate padding needed for right alignment against the panel width
        # Target width accounts for tree indentation (~4) and panel width
        target_width = panel_width + 4
        current_len = len(file_icon_text) + len(path_text)
        padding_needed = target_width - current_len - len(stats_text)
        padding = " " * max(0, padding_needed)
        file_label = Text.assemble(file_icon_text, path_text, padding, stats_text)

        file_node = tree.add(file_label)
        processed_files_count += 1

        # Use total_hunks_in_file from the first group (should be consistent)
        total_hunks_in_file = commit_groups[0].get("total_hunks_in_file", 0) if commit_groups else 0
        if total_hunks_in_file > 1:
            file_node.add(f" [hunk_info]Found {total_hunks_in_file} Hunks[/]")

        # Store the first commit message for this file (used in final summary)
        if commit_groups and "message" in commit_groups[0]:
            file_commit_messages[file_index] = commit_groups[0]["message"]

        for group_index_zero_based, group_data in enumerate(commit_groups):
            group_index_one_based = group_data.get(
                "group_index", group_index_zero_based + 1
            )  # Use stored or calculate
            total_groups = group_data.get("total_groups", len(commit_groups))
            message = group_data.get("message", "[Error: Message Missing]")

            if "(AI Error)" not in message and "(System Error)" not in message:
                total_commits_generated += 1
            num_hunks_in_group = group_data.get("num_hunks_in_group", "?")

            # --- Group Node Label (Right-aligned stats) ---
            group_icon_text = Text(" ", style="group_header")
            group_name_text = Text(
                f"Group {group_index_one_based} / {total_groups}",
                style="group_header",
            )
            group_stats_text = Text(f" {num_hunks_in_group}", style="hunk_info")
            # Calculate padding for right alignment against the panel width
            group_target_width = panel_width + 8  # Indentation ~8 for group level
            group_current_len = len(group_icon_text) + len(group_name_text)
            group_padding_needed = group_target_width - group_current_len - len(group_stats_text)
            group_padding = " " * max(0, group_padding_needed)
            group_label = Text.assemble(
                group_icon_text, group_name_text, group_padding, group_stats_text
            )

            group_node = file_node.add(group_label)

            # --- Commit Panel ---
            panel_title_text = "Message "
            panel_width = int(term_width * 0.75)
            title_padding_len = (
                panel_width - len(" ") - len(panel_title_text) - 4  # Account for borders/padding
            )
            title_padding = "─" * max(0, title_padding_len)

            panel_title = Text.assemble(
                (" ", "commit_title"),
                (title_padding, "commit_panel_border"),
                (" ", "default"),
                (panel_title_text, "commit_title"),
            )

            # Format commit message with indented word-wrapping
            commit_text_content = message
            indent = "      "  # 6 spaces for body indentation
            wrap_width = panel_width - 4  # Available width inside panel
            lines = commit_text_content.splitlines()
            title = lines[0] if lines else ""
            body_lines = lines[1:] if len(lines) > 1 else []

            wrapped_body = []
            for line in body_lines:
                leading_whitespace = ""
                stripped_line = line
                if line.startswith(("- ", "* ")):  # Common list markers
                    leading_whitespace = line[: line.find(line.lstrip())]
                    stripped_line = line.lstrip()

                wrapped_lines = textwrap.wrap(
                    stripped_line,
                    width=wrap_width - len(indent) - len(leading_whitespace),
                    initial_indent="",
                    subsequent_indent=indent + leading_whitespace,
                    replace_whitespace=False,
                    drop_whitespace=False,
                )
                if wrapped_lines:
                    wrapped_body.append(indent + leading_whitespace + wrapped_lines[0])
                    wrapped_body.extend(wrapped_lines[1:])

            formatted_content = title
            if wrapped_body:
                formatted_content += "\n\n" + "\n".join(wrapped_body)

            commit_text = Text(formatted_content, style="commit_message")

            commit_panel = Panel(
                commit_text,
                title=panel_title,
                title_align="left",
                border_style="commit_panel_border",
                box=ROUNDED,
                width=panel_width,
                expand=False,
            )
            group_node.add(commit_panel)
            # Store panel keyed by (file_index, group_index - 1 for 0-based access)
            commit_panels_to_update[(file_index, group_index_zero_based)] = commit_panel

    return (
        tree,
        commit_panels_to_update,
        file_commit_messages,
        processed_files_count,
        total_commits_generated,
    )
