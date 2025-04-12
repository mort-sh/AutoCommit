"""
Utility functions for cleaning and manipulating Git patch/diff text.
"""

import re
from typing import Any

from autocommit.utils.console import console


def clean_patch_format(patch_content: str) -> str:
    """
    Clean a patch to ensure it has exactly one valid header section.

    Args:
        patch_content: The patch content to clean

    Returns:
        A string with a properly formatted patch with one header section
    """
    # Split the patch into lines and analyze it
    lines = patch_content.splitlines(True)  # Keep line endings

    # Identify header patterns
    header_line_patterns = ["diff --git ", "index ", "--- ", "+++ "]

    # First pass: identify where header ends and first hunk starts
    header_lines = []
    first_hunk_index = -1

    for i, line in enumerate(lines):
        if line.startswith("@@ "):
            first_hunk_index = i
            break
        if any(line.startswith(pattern) for pattern in header_line_patterns):
            header_lines.append(line)

    # If no header found or no hunk found, return the original content
    if not header_lines or first_hunk_index == -1:
        return patch_content

    # Second pass: collect all hunks, ignoring any duplicate headers
    hunks = []
    i = first_hunk_index
    current_hunk = []

    while i < len(lines):
        line = lines[i]
        is_header_line = any(line.startswith(pattern) for pattern in header_line_patterns)
        is_hunk_line = line.startswith("@@ ")

        if is_header_line:
            # Skip header lines in the middle of the patch
            i += 1
            continue

        if is_hunk_line and current_hunk:
            # Start of a new hunk - save the current one and start fresh
            hunks.append("".join(current_hunk))
            current_hunk = [line]
        else:
            current_hunk.append(line)

        i += 1

    # Add the last hunk if there is one
    if current_hunk:
        hunks.append("".join(current_hunk))

    # Ensure the header ends with a newline
    header = "".join(header_lines)
    if not header.endswith("\\n"):
        header += "\\n"

    # Join everything together
    cleaned_patch = header + "".join(hunks)

    # Ensure patch ends with a newline
    if cleaned_patch and not cleaned_patch.endswith("\\n"):
        cleaned_patch += "\\n"

    return cleaned_patch


def create_patch_for_group(group_hunks: list[dict[str, Any]]) -> str:
    """
    Creates a combined diff string containing only the specified hunks.
    NOTE: This function ONLY joins the provided hunk diffs. Header must be prepended by caller.

    Args:
        group_hunks: A list of hunk dictionaries belonging to the target group.
                     Each hunk dict must contain at least the 'diff' key.

    Returns:
        A string containing the concatenated diff content of the hunks,
        or an empty string if no hunks are provided.
    """
    if not group_hunks:
        return ""

    # Combine the diff content of the specified hunks
    # Ensure each hunk has proper format with newlines between hunks
    patch_parts = []

    for hunk in group_hunks:
        hunk_diff = hunk["diff"].lstrip()  # Strip leading whitespace

        # Ensure each hunk starts with @@ and ends with a newline
        if not hunk_diff.startswith("@@ "):
            # Try to fix if it starts with just '@@'
            if hunk_diff.startswith("@@"):
                # Add the space if missing
                # Find the closing @@ to insert space correctly
                match = re.match(r"@@\\s*(-\\d+,\\d+)\\s+(\\+\\d+,\\d+)\\s*@@", hunk_diff)
                if match:
                    hunk_diff = f"@@ {match.group(1)} {match.group(2)} @@{hunk_diff[match.end() :]}"
                else:
                    # Fallback if regex fails, less precise
                    hunk_diff = "@@ " + hunk_diff[2:]
            else:
                console.print(
                    f"[debug]Warning:[/] Skipping invalid hunk fragment (doesn't start with @@): {hunk_diff[:80]}...",
                    style="warning",
                )
                continue  # Skip invalid hunks if it doesn't start with @@ at all

        if not hunk_diff.endswith("\\n"):
            hunk_diff += "\\n"
        patch_parts.append(hunk_diff)

    # Join with proper spacing between hunks
    patch_body = "".join(patch_parts)

    # Ensure trailing newline
    if patch_body and not patch_body.endswith("\\n"):
        patch_body += "\\n"

    return patch_body
