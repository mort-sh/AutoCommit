#!/usr/bin/env python3
"""
AI functionality for generating commit messages.
"""

import re
from typing import Any, List

import openai

from autocommit.core.constants import HUNK_CLASSIFICATION_PROMPT, SYSTEM_PROMPT
from autocommit.utils.console import console


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
    except Exception as e:
        console.print(f"Error generating commit message: {e}", style="warning")
        return "[Chore] Commit changes"


def classify_hunks(hunks: List[dict[str, Any]], model: str = "gpt-4o-mini") -> List[List[dict[str, Any]]]:
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

        # Debug: Print raw response
        # Check if debug mode is enabled (assuming args are passed or accessible)
        # This part needs refinement if args aren't directly available here.
        # For now, let's just print it unconditionally for testing.
        # TODO: Pass debug flag properly or use logging configuration
        console.print(f"DEBUG: Raw classify_hunks response:\n---\n{result}\n---", style="debug")

        # Extract the groups using regex - capture content inside brackets
        group_pattern = re.compile(r'GROUP \d+: \[(.*?)\]') # Capture content inside []
        matches = group_pattern.findall(result)

        # Convert to list of lists of hunks
        hunk_groups = []
        processed_hunk_indices = set() # Keep track of processed hunks
        for content_inside_brackets in matches:
            # Extract all numbers from the captured content (e.g., "HUNK 1, 3" -> ["1", "3"])
            numbers_found = re.findall(r'\d+', content_inside_brackets)
            hunk_indices = [int(num) - 1 for num in numbers_found] # Convert to 0-based index
            # Create a group with the hunks at those indices, ensuring no duplicates across groups
            group = []
            for idx in hunk_indices:
                if idx < len(hunks) and idx not in processed_hunk_indices:
                    group.append(hunks[idx])
                    processed_hunk_indices.add(idx)

            if group:  # Only add non-empty groups
                hunk_groups.append(group)

        # Add any remaining hunks that weren't assigned to a group by the AI into their own group
        remaining_hunks = [hunk for i, hunk in enumerate(hunks) if i not in processed_hunk_indices]
        if remaining_hunks:
            console.print("Warning: Some hunks were not explicitly grouped by AI. Placing them in a separate group.", style="warning")
            hunk_groups.append(remaining_hunks)

        # If no groups were found or all groups were empty, treat all hunks as one group
        if not hunk_groups:
            console.print("Warning: Failed to parse AI hunk classification or no groups found. Defaulting to single group.", style="warning")
            hunk_groups = [hunks]

        return hunk_groups
    except Exception as e:
        console.print(f"Error classifying hunks: {e}", style="warning")
        # If classification fails, treat all hunks as one group
        return [hunks]
