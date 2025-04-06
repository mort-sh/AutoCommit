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

        # Extract the groups using regex
        group_pattern = re.compile(r'GROUP \d+: \[([\d, ]+)\]')
        matches = group_pattern.findall(result)

        # Convert to list of lists of hunks
        hunk_groups = []
        for match in matches:
            # Parse the hunk indices, accounting for spaces after commas
            hunk_indices = [int(idx.strip()) - 1 for idx in match.split(',')]
            # Create a group with the hunks at those indices
            group = [hunks[idx] for idx in hunk_indices if idx < len(hunks)]
            if group:  # Only add non-empty groups
                hunk_groups.append(group)

        # If no groups were found or all groups were empty, treat all hunks as one group
        if not hunk_groups:
            hunk_groups = [hunks]

        return hunk_groups
    except Exception as e:
        console.print(f"Error classifying hunks: {e}", style="warning")
        # If classification fails, treat all hunks as one group
        return [hunks]
