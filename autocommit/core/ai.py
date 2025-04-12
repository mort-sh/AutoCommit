#!/usr/bin/env python3
"""
AI functionality for generating commit messages.
"""

import re
from typing import Any  # Added Dict

import openai
from rich.panel import Panel  # Import Panel for debug logging
from rich.text import Text  # Import Text for formatting

from autocommit.core.constants import HUNK_CLASSIFICATION_PROMPT, SYSTEM_PROMPT
from autocommit.utils.console import console


class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""

    pass


def _summarize_reasoning(reasoning: str) -> str:
    """Generates a short summary (<= 5 words) from reasoning text."""
    reasoning_lower = reasoning.lower()
    summary = "Grouped Logically"  # Default

    keywords = {
        "Error Handling Fix": ["error handling", "exception", "try", "except"],
        "Code Refactoring": [
            "refactor",
            "structure",
            "cleanup",
            "organize",
            "move",
            "consolidate",
            "encapsulate",
        ],
        "Feature Addition": ["feature", "add", "implement", "integrate", "introduce"],
        "Bug Fix": ["fix", "bug", "correct", "resolve", "issue"],
        "Test Update": ["test", "mock", "assert", "verify"],
        "Config Change": ["config", "setting", "parameter", "argument"],
        "Import Update": ["import"],
        "Logic Enhancement": ["logic", "enhance", "improve", "update"],
        "Doc Update": ["document", "comment", "docstring"],
        "Dependency Update": [
            "dependenc",
            "version",
            "library",
            "package",
        ],  # Handle dependency/dependencies
        "Style Formatting": ["style", "format", "lint", "indent"],
    }

    # Check keywords in rough order of specificity/impact
    for key, terms in keywords.items():
        if any(term in reasoning_lower for term in terms):
            summary = key
            break  # Use the first specific category found

    # Simple truncation if needed (though keywords are short)
    return f"**{summary}**"[:50]  # Limit length just in case


def generate_commit_message(diff: str, model: str = "gpt-4o-mini") -> str:
    """Generate a commit message using the OpenAI API."""
    try:
        client = openai.OpenAI()

        # For binary files or deleted files, use a simpler prompt
        if diff in {"Binary file", "File was deleted"}:
            file_status = "binary" if diff == "Binary file" else "deleted"
            user_prompt = f"This is a {file_status} file. Generate an appropriate commit message."
        else:
            user_prompt = (
                f"Please analyze this git diff and generate an appropriate commit message:\n\n"
                f"{diff}"
            )

        response = client.chat.completions.create(
            model=model,  # Use the specified model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        # Handle API errors (e.g., server errors, rate limits)
        console.print(f"OpenAI API Error: {e}", style="warning")
        raise OpenAIError(f"OpenAI API Error: {e}") from e
    except openai.AuthenticationError as e:
        # Handle authentication errors (invalid API key)
        console.print(f"OpenAI Authentication Error: {e}", style="warning")
        raise OpenAIError(f"OpenAI Authentication Error: {e}. Check your OPENAI_API_KEY.") from e
    except Exception as e:
        # Handle other potential errors (network issues, unexpected responses)
        console.print(f"Unexpected error during commit message generation: {e}", style="warning")
        raise OpenAIError(f"Unexpected error: {e}") from e


def classify_hunks(
    hunks: list[dict[str, Any]], model: str = "gpt-4o-mini", debug: bool = False
) -> list[list[int]]:
    """
    Classify hunks into logically related groups using the OpenAI API.

    Args:
        hunks: List of hunk dictionaries (each must contain 'diff').
        model: OpenAI model to use.
        debug: Whether to print debug information.

    Returns:
        List of groups, where each group is a list of original 0-based indices
        corresponding to the input hunks list.
        Raises OpenAIError on failure.
    """
    if not hunks:
        return []  # Return empty list if no hunks

    try:
        client = openai.OpenAI()

        # Prepare the prompt
        hunks_text = ""
        for i, hunk in enumerate(hunks, 1):  # Use 1-based index for prompt
            # Add original index marker for clarity in prompt if needed, but AI uses the HUNK number
            hunks_text += f"HUNK {i}:\n{hunk['diff']}\n\n"

        user_prompt = (
            f"Analyze the following {len(hunks)} code hunks from a single file and determine which ones are logically related "
            f"and should be committed together.\n\n{hunks_text}\n"
            f"Provide your answer STRICTLY in the following format, with each group on a new line:\n"
            f"GROUP: [list of 1-based hunk numbers separated by comma]\n"
            f"GROUP: [list of 1-based hunk numbers separated by comma]\n"
            f"...\n\n"
            f"Example:\nGROUP: [1, 3]\nGROUP: [2, 4, 5]\n\n"
            f"Do NOT include any reasoning or explanation, only the GROUP lines."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": HUNK_CLASSIFICATION_PROMPT,
                },  # Keep system prompt for general guidance
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1000,  # Adjust tokens if needed based on hunk count
        )
        # Parse the response
        result = response.choices[0].message.content.strip()

        # Debug: Print raw response only if debug mode is enabled
        if debug:
            console.print(
                Panel(
                    result,
                    title="[debug]Raw AI Hunk Classification Response[/]",
                    border_style="dim blue",
                ),
                style="debug",
            )

        # --- Parsing for GROUP lines ---
        grouped_indices: list[list[int]] = []
        processed_hunk_indices = set()  # Track indices assigned to groups

        # Find all GROUP lines using regex
        group_lines = re.findall(r"^GROUP:\s*\[(.*?)\]\s*$", result, re.MULTILINE | re.IGNORECASE)

        for line_content in group_lines:
            # Extract comma-separated numbers within the brackets
            numbers_found = re.findall(r"\d+", line_content)
            current_group_indices = []
            for num_str in numbers_found:
                try:
                    hunk_index_1_based = int(num_str)
                    hunk_index_0_based = hunk_index_1_based - 1
                    # Validate index and ensure not already processed
                    if 0 <= hunk_index_0_based < len(hunks):
                        # Allow adding to group even if processed, handle unique later if needed
                        # For now, just add valid indices
                        current_group_indices.append(hunk_index_0_based)
                        processed_hunk_indices.add(hunk_index_0_based)
                    elif debug:
                        console.print(
                            f"[debug]Warning:[/] Invalid hunk index {hunk_index_1_based} found in AI response.",
                            style="warning",
                        )
                except ValueError:
                    if debug:
                        console.print(
                            f"[debug]Warning:[/] Non-integer value '{num_str}' found in AI group list.",
                            style="warning",
                        )

            # Add the group if it contains valid indices
            if current_group_indices:
                # Ensure indices within the group are unique before adding
                unique_indices = sorted(list(set(current_group_indices)))
                grouped_indices.append(unique_indices)

        # --- Handle Ungrouped Hunks ---
        # Add any remaining hunks that weren't assigned to any group into a final separate group
        remaining_indices = []
        for i in range(len(hunks)):
            if i not in processed_hunk_indices:
                remaining_indices.append(i)

        if remaining_indices:
            if debug:
                console.print(
                    f"[debug]DEBUG:[/] Adding {len(remaining_indices)} unclassified hunk(s) to a separate group.",
                    style="debug",
                )
            grouped_indices.append(remaining_indices)

        # If parsing failed or no groups were found, treat all hunks as one group
        if not grouped_indices and hunks:
            console.print(
                "Warning: Failed to parse AI hunk classification or no groups found. Defaulting to single group.",
                style="warning",
            )
            grouped_indices = [list(range(len(hunks)))]

        return grouped_indices
    except openai.APIError as e:
        console.print(f"OpenAI API Error during hunk classification: {e}", style="warning")
        raise OpenAIError(f"OpenAI API Error during hunk classification: {e}") from e
    except openai.AuthenticationError as e:
        console.print(
            f"OpenAI Authentication Error during hunk classification: {e}", style="warning"
        )
        raise OpenAIError(f"OpenAI Authentication Error: {e}. Check your OPENAI_API_KEY.") from e
    except Exception as e:
        console.print(f"Unexpected error during hunk classification: {e}", style="warning")
        # If classification fails due to unexpected error, maybe still return default?
        # Or raise? Let's raise for now to make failures explicit.
        raise OpenAIError(f"Unexpected error during hunk classification: {e}") from e
