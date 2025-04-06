# AutoCommit Refactoring Plan

## 1. Introduction

This document outlines a plan for refactoring the `autocommit` project. The goals are to improve code structure, maintainability, testability, and prepare the codebase for potential future enhancements, such as a graphical user interface (UI). The refactoring will focus on applying SOLID principles, improving separation of concerns, and consolidating utility functions.

## 2. Current State Assessment (Summary)

An initial inventory assessment revealed the following structure and potential areas for improvement:

*   **Project Structure:** Organized into `cli`, `core`, and `utils` modules. `main.py` serves as the entry point.
*   **Core Logic (`core/`):**
    *   `processor.py`: Central orchestrator, handles parallel processing, file processing logic. Appears complex.
    *   `ai.py`: Handles OpenAI API interactions (message generation, hunk classification).
    *   `diff.py`: Implements diff parsing and chunking based on atomicity levels.
    *   `files.py`: Handles Git status parsing, identifying changed/untracked files, getting file diffs, `.gitignore` interaction.
    *   `commit.py`: Primarily handles `git push`. Actual commit creation logic needs clarification.
    *   `constants.py`: Holds constant values.
*   **CLI (`cli/`):**
    *   `cli.py`: Handles argument parsing (`argparse`) and the main execution flow initiation.
*   **Utilities (`utils/`):**
    *   `git.py`: Low-level wrapper for executing `git` commands.
    *   `console.py`: Likely sets up `rich` for console output.
    *   `file.py`: Contains an `is_binary` function, potentially redundant with `core/files.py`.
*   **Redundancy:** `is_binary` function exists in both `core/files.py` and `utils/file.py`.
*   **Dependencies:** `openai`, `argparse`, `rich`. Dev: `pytest`, `ruff`, `pyinstaller`. Build: `hatchling`, `uv`.

## 3. Proposed Refactoring Strategy

The refactoring will address the following key areas:

### 3.1. Consolidate Utilities & Clarify `core` vs. `utils`
    *   **Action:** Merge redundant functions (e.g., `is_binary`).
    *   **Action:** Define clear boundaries: `utils` for generic, low-level helpers (like the Git command runner, console setup), `core` for application-specific logic. Move functions accordingly.

### 3.2. Refine Git Interaction Layer
    *   **Action:** Improve separation between high-level Git logic (status interpretation, file handling in `core/files.py`) and low-level command execution (`utils/git.py`).
    *   **Action:** Explicitly locate and potentially encapsulate the `git add` and `git commit` command execution logic. Consider a dedicated `GitRepository` class in `core` or `utils`.
    *   **Action:** Refactor `core/commit.py` to focus solely on pushing, or integrate its logic into the main processing flow if simpler.

### 3.3. Simplify Core Processor (`processor.py`)
    *   **Action:** Apply the Single Responsibility Principle (SRP) by breaking down `processor.py` into smaller, more focused functions or classes.
    *   **Action:** Identify distinct stages: file discovery, diff generation, chunking, AI processing, commit application. Encapsulate these stages.
    *   **Action:** Manage state (like processed files, generated messages) more explicitly, potentially using data classes or a central state object.

### 3.4. Decouple Core Logic from CLI
    *   **Action:** Modify core functions (`process_files`, `generate_commit_message`, etc.) to accept necessary parameters directly instead of relying on the `argparse.Namespace` object.
    *   **Action:** Ensure core modules return results rather than directly printing or exiting (delegate output to the CLI layer or console utility). This facilitates testing and reuse (e.g., by a future UI).

### 3.5. Centralize Configuration
    *   **Action:** Create a dedicated configuration module or class to manage settings like OpenAI model, API key (retrieval), chunk level, parallelism, etc.
    *   **Action:** Pass configuration objects/values explicitly to functions needing them, avoiding global state or excessive argument drilling.

### 3.6. Improve Error Handling
    *   **Action:** Systematically review error handling for `git` command execution (`utils/git.py`) and OpenAI API calls (`core/ai.py`).
    *   **Action:** Define custom exception types for specific error conditions (e.g., `GitCommandError`, `OpenAIError`).
    *   **Action:** Ensure errors are propagated appropriately and handled gracefully at the CLI level, providing informative messages to the user.

### 3.7. Enhance Testability
    *   **Action:** Improve modularity through the decoupling steps above.
    *   **Action:** Introduce dependency injection where appropriate (e.g., injecting Git runner, AI client).
    *   **Action:** Write unit tests for refactored components, mocking external dependencies (Git commands, OpenAI API).
    *   **Action:** Add integration tests for key workflows.

## 4. Future UI Considerations

The decoupling of core logic from the CLI (Section 3.4) is the primary step to enable future UI development. A UI (e.g., using Tkinter, PyQt, or a web framework) could interact with the refactored core modules by:

*   Calling functions like `get_uncommitted_files` to display changes.
*   Invoking `process_files` (or its refactored equivalent) with appropriate configuration.
*   Displaying generated commit messages and allowing user review/editing before applying commits.
*   Providing visual feedback on progress and errors.

## 5. Detailed Steps (To Be Added)

*(This section will be populated with more granular steps as the refactoring progresses.)*
