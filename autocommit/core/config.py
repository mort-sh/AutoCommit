#!/usr/bin/env python3
"""
Configuration settings for AutoCommit.
"""

from dataclasses import dataclass, field
import os

from autocommit.utils.console import console


@dataclass
class Config:
    """Holds application configuration settings."""

    model: str = "gpt-4o-mini"
    chunk_level: int = 2
    parallel: int = 0  # 0 means auto
    test_mode: int | None = None  # None means not test mode, int is file limit
    push: bool = False
    remote: str = "origin"
    branch: str | None = None  # None means current branch
    debug: bool = False
    auto_track: bool = False
    openai_api_key: str | None = field(
        default=None, init=False, repr=False
    )  # Don't show key in repr, get in post_init

    def __post_init__(self):
        """Retrieve API key and validate settings after initialization."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            # Log a warning, the AI module will raise an error if it's actually needed
            console.print("Warning: OPENAI_API_KEY environment variable not set.", style="warning")

        # Ensure branch is None if empty string was passed during init (e.g., from argparse default)
        if not self.branch:
            self.branch = None

        # Validate chunk_level
        if not 0 <= self.chunk_level <= 3:
            raise ValueError("chunk_level must be between 0 and 3")

        # Validate parallel
        if self.parallel < 0:
            raise ValueError("parallel level cannot be negative")

    def get_chunk_level_description(self) -> str:
        """Returns a human-readable description for the chunk level."""
        if self.chunk_level == 0:
            return "file level"
        elif self.chunk_level == 1:
            return "hunk level"
        elif self.chunk_level == 2:
            return "logical units"
        elif self.chunk_level == 3:
            return "semantic context"
        else:
            return "unknown"
