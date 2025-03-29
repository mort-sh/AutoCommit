#!/usr/bin/env python3
"""
Utility functions for file operations.
"""

from pathlib import Path

# Constants for binary detection and file size limits
MAX_FILE_SIZE = 1024 * 1024  # 1MB
BINARY_CHECK_SIZE = 8000  # Check first 8KB for binary content
BINARY_THRESHOLD = 0.3  # 30% non-text characters
TEXT_CHARS = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})


def is_binary(file_path: Path) -> bool:
    """Check if a file is binary by examining its contents."""
    try:
        # Default result if we can't process properly
        is_binary_file = True

        if file_path.exists():
            # Check file size if possible
            try:
                if file_path.stat().st_size <= MAX_FILE_SIZE:
                    # Only process if file is small enough
                    try:
                        with open(file_path, "rb") as f:
                            chunk = f.read(BINARY_CHECK_SIZE)

                        # Empty files are not binary
                        if chunk:
                            # Count non-text characters
                            non_text_count = sum(1 for byte in chunk if byte not in TEXT_CHARS)
                            # Calculate the ratio of non-text characters
                            non_text_ratio = non_text_count / len(chunk)
                            is_binary_file = non_text_ratio > BINARY_THRESHOLD
                        else:
                            is_binary_file = False
                    except PermissionError:
                        # For permission errors on read, assume text file
                        is_binary_file = False
            except PermissionError:
                # If we can't get stats but file exists, try to read it anyway
                is_binary_file = False
        else:
            # File doesn't exist
            is_binary_file = False

        return is_binary_file
    except Exception:
        # For other errors, assume binary to be safe
        return True
