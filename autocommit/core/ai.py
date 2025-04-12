#!/usr/bin/env python3
"""
AI functionality for generating commit messages.
"""

import re
from typing import Any  # Added Dict

import openai
from rich.panel import Panel  # Import Panel for debug logging

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
) -> list[list[dict[str, Any]]]:
    """
    Classify hunks into logically related groups using the OpenAI API.

    Args:
        hunks: List of hunks to classify
        model: OpenAI model to use

    Returns:
        List of groups of related hunks
    """
    try:
        client = openai.OpenAI()

        # Prepare the prompt
        hunks_text = ""
        for i, hunk in enumerate(hunks, 1):
            hunks_text += f"HUNK {i}:\n{hunk['diff']}\n\n"

        user_prompt = (
            f"Analyze the following code hunks from a single file and determine which ones are logically related "
            f"and should be committed together.\n\n{hunks_text}\n"
            f"For each hunk, assign it to a logical group. Hunks that are part of the same feature, fix the same bug, "
            f"or are otherwise logically related should be in the same group.\n\n"
            f"Provide your answer in the following format:\n"
            f"GROUP 1: [list of hunk numbers]\n"
            f"GROUP 2: [list of hunk numbers]\n"
            f"...\n\n"
            f"Explain your reasoning for each group."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": HUNK_CLASSIFICATION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1000,
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

        # --- Enhanced Parsing for Groups and Reasoning ---
        hunk_groups = []
        group_reasonings: dict[int, str] = {}  # Store reasoning per group index (1-based)
        processed_hunk_indices = set()

        # Split response into potential group sections
        group_sections = re.split(r"GROUP \d+:", result, flags=re.IGNORECASE)

        if len(group_sections) > 1:
            # Process each section (index 0 is usually preamble)
            for i, section in enumerate(group_sections[1:], 1):
                # Extract hunk numbers (e.g., from "[1, 3, 5]")
                hunk_match = re.search(r"\[(.*?)\]", section)
                reasoning_text = ""
                if hunk_match:
                    numbers_found = re.findall(r"\d+", hunk_match.group(1))
                    hunk_indices = [int(num) - 1 for num in numbers_found]  # 0-based

                    # Extract reasoning (look for '**Reasoning:**' or similar)
                    reasoning_match = re.search(
                        r"\*\*Reasoning:\*\*(.*)", section, re.IGNORECASE | re.DOTALL
                    )
                    if reasoning_match:
                        reasoning_text = reasoning_match.group(1).strip()
                    else:  # Fallback if specific marker not found
                        # Try taking text after the hunk list bracket
                        bracket_end_pos = hunk_match.end()
                        reasoning_text = section[bracket_end_pos:].strip()

                    group_reasonings[i] = reasoning_text  # Store reasoning

                    # Create group, avoiding duplicates
                    group = []
                    for idx in hunk_indices:
                        if idx < len(hunks) and idx not in processed_hunk_indices:
                            group.append(hunks[idx])
                            processed_hunk_indices.add(idx)
                    if group:
                        hunk_groups.append(group)
                else:
                    console.print(
                        f"[debug]Warning:[/] Could not parse hunks for Group {i} section.",
                        style="warning",
                    )

        # Fallback if regex parsing failed completely
        if not hunk_groups and len(hunks) > 0:
            console.print(
                "[debug]Warning:[/] Failed to parse AI groups via regex, treating all hunks as one group.",
                style="warning",
            )
            hunk_groups = [hunks]
            group_reasonings[1] = "Fallback - Grouping failed"  # Add default reasoning

        # --- Print Concise Summaries ---
        if len(hunk_groups) > 1:  # Only print summaries if more than one group
            console.print("\n[bold white]AI Grouping Summary:[/bold white]")
            for i, group in enumerate(hunk_groups, 1):
                reason = group_reasonings.get(i, "No reasoning provided.")
                summary = _summarize_reasoning(reason)  # Keep existing summary logic
                num_hunks = len(group)
                hunk_text = f"{num_hunks} hunk" if num_hunks == 1 else f"{num_hunks} hunks"
                # Use suggested rich formatting
                console.print(f"- [bold]Group {i}[/bold] ([cyan]{hunk_text}[/cyan]): {summary}")
            console.print("-" * 20)  # Separator

        # Print raw response in panel only if debug mode is enabled
        if debug:
            console.print(
                Panel(
                    result,
                    title="[debug]Raw AI Hunk Classification Response[/]",
                    border_style="dim blue",
                ),
                style="debug",
            )

        # Add any remaining hunks that weren't assigned
        processed_hunk_indices = set()  # Keep track of processed hunks
        # (Logic moved above inside the enhanced parsing loop)

        # Add any remaining hunks that weren't assigned to a group by the AI into their own group
        remaining_hunks = [hunk for i, hunk in enumerate(hunks) if i not in processed_hunk_indices]
        if remaining_hunks:
            if debug:  # Only print warning in debug mode
                console.print(
                    "[debug]Warning:[/] Some hunks were not explicitly grouped by AI. Placing them in a separate group.",
                    style="warning",
                )
            hunk_groups.append(remaining_hunks)

        # If no groups were found or all groups were empty, treat all hunks as one group
        if not hunk_groups:
            console.print(
                "Warning: Failed to parse AI hunk classification or no groups found. Defaulting to single group.",
                style="warning",
            )
            hunk_groups = [hunks]

        return hunk_groups
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
