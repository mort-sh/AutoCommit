#!/usr/bin/env python3
"""
AI functionality for generating commit messages.
"""

import openai

from autocommit.core.constants import SYSTEM_PROMPT
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
