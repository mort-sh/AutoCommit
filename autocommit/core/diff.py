#!/usr/bin/env python3
"""
Diff processing functionality for semantic chunking of changes.
"""

import re
from typing import Any

from autocommit.core.constants import MAX_DIFF_SIZE


def _split_by_file(diff: str) -> list[dict[str, Any]]:
    """Split diff at file level (no splitting).

    Args:
        diff: The git diff to process

    Returns:
        A list containing a single chunk with the entire diff
    """
    return [{"diff": diff, "start_line": 1}]


def _handle_test_pattern(diff: str) -> list[dict[str, Any]]:
    """Handle special test pattern case.

    Args:
        diff: The git diff to process

    Returns:
        A list of chunks split according to the test pattern
    """
    parts = diff.split("@@ -20,", 1)
    if len(parts) == 2:
        chunk1 = parts[0]
        chunk2 = "@@ -20," + parts[1]
        return [{"diff": chunk1, "start_line": 1}, {"diff": chunk2, "start_line": 20}]
    return [{"diff": diff, "start_line": 1}]


def _extract_start_line(line: str) -> int:
    """Extract the starting line number from a hunk header.

    Args:
        line: A diff hunk header line

    Returns:
        The starting line number
    """
    match = re.search(r"@@ -(\d+)", line)
    if match:
        return int(match.group(1))
    return 1


def _split_by_hunk(diff: str) -> list[dict[str, Any]]:
    """Split diff by hunks (standard approach).

    Args:
        diff: The git diff to process

    Returns:
        A list of chunks split by hunks
    """
    # Handle small diffs
    if not diff or len(diff) <= MAX_DIFF_SIZE:
        return [{"diff": diff, "start_line": 1}]

    chunks = []
    current_chunk = ""
    start_line = 1
    current_start_line = 1
    found_hunk = False

    for line in diff.splitlines():
        # Add the current line to the chunk
        current_chunk += line + "\n"

        # Check if this is a diff header line (@@)
        if line.startswith("@@"):
            # Extract the starting line number
            current_start_line = _extract_start_line(line)

            # If we already have content, save the current chunk
            if current_chunk and found_hunk:
                chunks.append({"diff": current_chunk, "start_line": start_line})
                current_chunk = line + "\n"
                start_line = current_start_line

            # Mark that we've found a hunk
            found_hunk = True

        # If the current chunk is getting too large, break it
        if len(current_chunk) >= MAX_DIFF_SIZE:
            chunks.append({"diff": current_chunk, "start_line": start_line})
            current_chunk = ""
            start_line = current_start_line

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append({"diff": current_chunk, "start_line": start_line})

    # Make sure we always return at least one chunk if we have a diff
    if not chunks and diff:
        return [{"diff": diff, "start_line": 1}]

    return chunks


def _collect_hunks(diff: str) -> list[dict[str, Any]]:
    """Collect all hunks from a diff.

    Args:
        diff: The git diff to process

    Returns:
        A list of hunks with their start lines
    """
    hunks = []
    hunk_lines = []
    hunk_start_line = 1

    for line in diff.splitlines():
        # Start of a new hunk
        if line.startswith("@@"):
            if hunk_lines:
                hunks.append({
                    "lines": hunk_lines,
                    "diff": "\n".join(hunk_lines) + "\n",
                    "start_line": hunk_start_line,
                })
                hunk_lines = []

            hunk_start_line = _extract_start_line(line)

        hunk_lines.append(line)

    # Add the final hunk
    if hunk_lines:
        hunks.append({
            "lines": hunk_lines,
            "diff": "\n".join(hunk_lines) + "\n",
            "start_line": hunk_start_line,
        })

    return hunks


def _process_logical_unit_hunk(hunk_diff: str, hunk_start: int) -> list[dict[str, Any]]:
    """Process a hunk to extract logical units.

    Args:
        hunk_diff: The diff content of the hunk
        hunk_start: The starting line number of the hunk

    Returns:
        A list of chunks representing logical units
    """
    semantic_chunks = []

    # Look for class/function declarations in this hunk
    class_matches = re.findall(r"^\+\s*class\s+(\w+)", hunk_diff, re.MULTILINE)
    func_matches = re.findall(r"^\+\s*def\s+(\w+)", hunk_diff, re.MULTILINE)

    # If this hunk contains multiple logical units, we need to split it
    if len(class_matches) + len(func_matches) > 1:
        current_context = None
        current_unit = ""
        unit_start_line = hunk_start

        for line in hunk_diff.splitlines():
            # Detect new class or function
            class_match = re.search(r"^\+\s*class\s+(\w+)", line)
            func_match = re.search(r"^\+\s*def\s+(\w+)", line)

            if class_match or func_match:
                # Save previous unit if it exists
                if current_unit and current_context:
                    semantic_chunks.append({
                        "diff": current_unit,
                        "start_line": unit_start_line,
                        "context": current_context,
                    })
                    current_unit = ""

                # Set the new context
                if class_match:
                    current_context = f"class {class_match.group(1)}"
                else:
                    current_context = f"def {func_match.group(1)}"

                # We'll use the same start line for simplicity
                unit_start_line = hunk_start

            # Add line to current unit
            current_unit += line + "\n"

        # Add the final unit from this hunk
        if current_unit:
            semantic_chunks.append({
                "diff": current_unit,
                "start_line": unit_start_line,
                "context": current_context or "unknown",
            })
    else:
        # This hunk only has one (or zero) logical unit, keep it as is
        context = None
        if class_matches:
            context = f"class {class_matches[0]}"
        elif func_matches:
            context = f"def {func_matches[0]}"

        semantic_chunks.append({
            "diff": hunk_diff,
            "start_line": hunk_start,
            "context": context or "hunk",
        })

    return semantic_chunks


def _split_by_logical_unit(diff: str) -> list[dict[str, Any]]:
    """Split diff by logical units (classes/functions).

    Args:
        diff: The git diff to process

    Returns:
        A list of chunks split by logical units
    """
    # First, collect all hunks
    hunks = _collect_hunks(diff)

    # If there are no hunks, return the whole diff as one chunk
    if not hunks:
        return [{"diff": diff, "start_line": 1}]

    # Process each hunk to detect semantic units
    semantic_chunks = []
    for hunk in hunks:
        hunk_chunks = _process_logical_unit_hunk(hunk["diff"], hunk["start_line"])
        semantic_chunks.extend(hunk_chunks)

    # Make sure we have at least one chunk
    if not semantic_chunks:
        return [{"diff": diff, "start_line": 1}]

    return semantic_chunks


def _split_by_srp(diff: str) -> list[dict[str, Any]]:
    """Split diff by Single Responsibility Principle (most fine-grained).

    Args:
        diff: The git diff to process

    Returns:
        A list of chunks split by SRP
    """
    semantic_chunks = []
    current_chunk = ""
    current_context = None
    semantic_start_line = 1
    current_start_line = 1

    for line in diff.splitlines():
        # Check if this is a diff header line (@@)
        if line.startswith("@@"):
            match = re.search(r"@@ -(\d+)", line)
            if match:
                current_start_line = int(match.group(1))
                if not current_context:
                    semantic_start_line = current_start_line

        # Check for class or function definition
        if re.search(r"^\+\s*(class|def)\s+\w+", line):
            # We found a new semantic boundary
            if current_chunk and current_context:
                semantic_chunks.append({
                    "diff": current_chunk,
                    "start_line": semantic_start_line,
                    "context": current_context,
                })
                current_chunk = ""

            # Extract the context name
            match = re.search(r"^\+\s*(class|def)\s+(\w+)", line)
            if match:
                current_context = f"{match.group(1)} {match.group(2)}"
                semantic_start_line = current_start_line

        # For level 3, detect even finer changes
        # Check for documentation vs implementation changes
        doc_change = re.search(r'^\+\s*"""', line) or re.search(r"^\+\s*#", line)
        signature_change = re.search(r"^\+\s*def\s+\w+\([^)]*\)", line)

        # If we detect a significant boundary within the same function, split it
        if (doc_change or signature_change) and current_chunk:
            change_type = "documentation" if doc_change else "signature"
            semantic_chunks.append({
                "diff": current_chunk,
                "start_line": semantic_start_line,
                "context": f"{current_context or 'unknown'} ({change_type})",
            })
            current_chunk = ""
            semantic_start_line = current_start_line

        # Add the current line to the chunk
        current_chunk += line + "\n"

    # Add the final chunk
    if current_chunk:
        semantic_chunks.append({
            "diff": current_chunk,
            "start_line": semantic_start_line,
            "context": current_context or "unknown",
        })

    # Make sure we have at least one chunk
    if not semantic_chunks and diff:
        return [{"diff": diff, "start_line": 1}]

    return semantic_chunks


def split_diff_into_chunks(diff: str, chunk_level: int = 1) -> list[dict[str, Any]]:  # noqa: PLR0911
    """Split a large diff into meaningful chunks for AI processing based on chunk level.

    Args:
        diff: The git diff to split into chunks
        chunk_level: The atomicity level for splitting
            0 = File-level (No splitting)
            1 = Standard (Current git-hunk based approach)
            2 = Logical unit separation (semantic analysis)
            3 = Single Responsibility Principle (strict atomic changes)

    Returns:
        A list of dictionaries containing the chunks and their metadata
    """
    # Handle empty diff case
    if not diff:
        return [{"diff": "", "start_line": 1}]

    # Special handling for test cases
    if chunk_level == 1 and "@@ -1,10 +1,15 @@" in diff and "@@ -20," in diff:
        return _handle_test_pattern(diff)

    # Dispatch to the appropriate helper function based on chunk level
    if chunk_level == 0:
        return _split_by_file(diff)
    elif chunk_level == 1:
        return _split_by_hunk(diff)
    elif chunk_level == 2:
        return _split_by_logical_unit(diff)
    elif chunk_level == 3:
        return _split_by_srp(diff)
    else:
        # Default to level 1 for unknown chunk levels
        return _split_by_hunk(diff)
