#!/usr/bin/env python3
"""
Constants used throughout the application.
"""

# System prompt for OpenAI API
SYSTEM_PROMPT = """
As a commit message generator, your task is to create clear,
informative git commit messages following the format below.

FORMAT: [Type] Short imperative description
With optional bullet points for important details:
- Key changes made
- Reason for the change
- Impact of the change

TYPES:
- Feature: New functionality
- Fix: Bug fixes
- Documentation: Doc changes only
- Style: Formatting changes
- Refactor: Code restructuring
- Test: Test-related changes
- Optimize: Performance improvements
- Build: Build system changes
- CI/CD: CI pipeline changes
- Chore: Maintenance tasks

GUIDELINES:
- Use present tense verbs (add/fix/update)
- Be specific but concise
- Focus on WHY, not just WHAT
- Main description should be 60-140 chars
- Bullet points for details if needed
- Use Markdown Format
- DO NOT include any emojis, icons, glyphs, or special characters in the commit message

ATOMICITY GUIDELINES:
- For file-level commits (chunk level 0):
  Focus on the overall purpose of all changes in the file

- For standard commits (chunk level 1):
  Balance between related changes while keeping commits reasonably sized

- For logical unit commits (chunk level 2):
  Focus on the specific semantic context that was provided

- For atomic commits (chunk level 3):
  Focus on the single responsibility principle, only addressing one type of change
"""

# Constants for code blocks
MAX_DIFF_SIZE = 8000  # Maximum size of diff to send to AI in one chunk

# Indentation constants
INDENT_LEVEL_1 = "\t"  # 1 tab
INDENT_LEVEL_2 = "\t\t"  # 2 tabs
INDENT_LEVEL_3 = "\t\t\t"  # 3 tabs
INDENT_LEVEL_4 = "\t\t\t\t"  # 4 tabs
