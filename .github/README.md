
<span align="center">

# AutoCommit

AI-powered Git commit message generator that automates commit messages using OpenAI's API, featuring atomic commits based on logical code groups.

<img src="logo.png" alt="AutoCommit Logo">
</span>

## Features

-   Automatically generates meaningful commit messages for changed files using OpenAI.
-   **Atomic Commits:** Creates separate commits for logically related code groups within files, not just per-file.
-   **Configurable Granularity:** Control commit atomicity using `--chunk-level` (file, hunk, logical unit, or single responsibility).
-   Handles binary files, deleted files, and untracked files (interactively or automatically).
-   Optionally pushes commits after creation.
-   Customizable OpenAI model selection.
-   Parallel processing for faster analysis and message generation.
-   Rich terminal output with detailed commit plans and summaries, including file trees.

## Requirements

-   Python 3.12 or higher
-   OpenAI API key set in your environment variables (`OPENAI_API_KEY`)
-   Git installed and accessible from the command line
-   [UV package manager](https://github.com/astral-sh/uv) (recommended for installation and running scripts)

## Installation

### With UV (recommended)

```bash
git clone https://github.com/mort-sh/AutomaticGitCommit.git
cd AutomaticGitCommit
uv pip install -e .
```

### With pip

```bash
git clone https://github.com/mort-sh/AutomaticGitCommit.git
cd AutomaticGitCommit
pip install -e .
```

## Usage

Before using AutoCommit, set your OpenAI API key:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

To analyze changes, generate a commit plan, and apply commits:

```bash
autocommit
```

### Key Options

```
autocommit [OPTIONS]

Options:
  --test N          Test mode: analyze changes and display the commit plan
                    without applying commits. Optionally limit analysis to N files.
                    If N is omitted, defaults to analyzing 1 file.
  --push            Push commits to the remote after creation.
  --remote REMOTE   Remote repository to push to (default: origin).
  --branch BRANCH   Branch to push to (defaults to the current branch).
  --model MODEL     OpenAI model to use for generation (default: gpt-4o-mini).
  --chunk-level {0,1,2,3}
                    Control commit atomicity level (default: 2):
                      0 = Coarse (one commit per file)
                      1 = Standard (commits based on git hunks/size)
                      2 = Fine (commits per logical unit like function/class)
                      3 = Atomic (commits per single responsibility change)
  --parallel N      Set parallelism level for AI calls:
                      0 = Auto (uses CPU count, default)
                      N = Use N concurrent workers
  --auto-track      Automatically stage all untracked files without prompting.
  --debug           Enable detailed debug logging output.
  -h, --help        Show this help message and exit.
```

### Handling Untracked Files

When AutoCommit detects untracked files (unless `--auto-track` is used), it will interactively prompt you for each one:

```
Untracked file: [bold]path/to/new_file.py[/bold]
[A]dd file, [I]gnore file (add to .gitignore), [S]kip file, or [AA] Add all untracked files:
```

-   **A (Add):** Stage this file for commit processing.
-   **I (Ignore):** Add the file/pattern to `.gitignore` and skip it.
-   **S (Skip):** Do not stage or ignore this file for this run.
-   **AA (Add All):** Stage this file and all subsequent untracked files in this run without further prompts.

### Commit Atomicity Levels (`--chunk-level`)

This option controls how AutoCommit groups changes into commits:

-   **Level 0: Coarse (File Level)**
    -   Generates **one commit per modified file**.
    -   Ignores logical relationships *within* a file.
    *   Suitable for bulk changes or when file-level history is sufficient.

-   **Level 1: Standard (Hunk/Size Based)**
    -   Splits changes based on standard `git diff` hunks and size limits.
    *   Aims for reasonably sized commits but may group unrelated changes within a hunk.

-   **Level 2: Fine (Logical Units - Default)**
    -   Uses AI to identify logically related hunks (e.g., changes within the same function or class).
    -   Generates **separate commits for each identified logical group**, even within the same file.
    *   Provides a good balance between atomicity and context.

-   **Level 3: Atomic (Single Responsibility)**
    -   Attempts the finest granularity, trying to isolate individual responsibilities (e.g., refactoring vs. logic change vs. doc update) into separate commits.
    *   Relies heavily on AI classification and may result in many small commits.

### Examples

Preview the commit plan for the first modified file without committing:
```bash
autocommit --test 1
# or simply:
autocommit --test
```

Analyze all files and generate commits, then push:
```bash
autocommit --push
```

Use a more powerful model and create commits based on logical units (default level):
```bash
autocommit --model gpt-4o
```

Generate highly atomic commits based on single responsibility:
```bash
autocommit --chunk-level 3
```

Run with 8 parallel workers for AI calls:
```bash
autocommit --parallel 8
```

Automatically stage all new files and commit:
```bash
autocommit --auto-track
```

Enable debug output for detailed logs:
```bash
autocommit --debug
```

## How It Works

1.  **Scan:** Checks for uncommitted changes using `git status`.
2.  **Untracked Files:** Handles untracked files based on user input or `--auto-track`.
3.  **Diff:** Gets file diffs relative to `HEAD` (`git diff HEAD`).
4.  **Chunking:** Splits diffs into hunks.
5.  **Classification:** Uses the selected OpenAI model (`--model`) to analyze hunks (based on `--chunk-level`) and identify logically related groups, returning groups of hunk indices.
6.  **Patch & Message Generation:** For each identified group:
    *   Generates a conventional commit message via OpenAI.
    *   Constructs a precise `git apply`-compatible patch containing only the hunks for that group.
7.  **Plan Preview:** Displays a tree visualizing the files and the planned commit groups with their generated messages.
8.  **Commit Application (if not `--test`):**
    *   Iterates through each file and planned commit group.
    *   For modified files with multiple groups:
        *   Resets the git index for the file (`git reset HEAD`).
        *   Applies the specific group's patch to the index (`git apply --cached`).
        *   Creates the commit (`git commit`).
    *   For whole-file changes (new, deleted, binary, single-group): Stages the file (`git add`) and commits.
9.  **Summary:** Displays a final summary tree showing which files were successfully committed.
10. **Push (Optional):** If `--push` is enabled and commits were made, pushes to the specified remote/branch (`git push`).

## Development Scripts

Utility scripts are provided for development, using the [UV package manager](https://github.com/astral-sh/uv).

**Install development dependencies first:**
```bash
uv pip install -e ".[dev]"
```

**Run scripts using `uv run`:**

-   **Build:** Creates Python packages (`.whl`) and optionally platform executables.
    ```bash
    # Build wheel only
    uv run project_build

    # Build wheel and executable
    uv run project_build --executable
    ```
    *Output in `dist/` directory.*

-   **Clean:** Removes build artifacts, caches (`__pycache__`, `.pytest_cache`, etc.), and UV cache.
    ```bash
    uv run project_clean
    ```

-   **Release Helper:** Automates version bumping and PR creation for releases.
    ```bash
    uv run project_release
    ```
    *Checks `origin/main`, bumps patch version in `pyproject.toml` if needed, runs tests, builds, creates a `release/vX.Y.Z` branch, commits version bump, pushes branch, attempts GitHub PR creation, and provides instructions for tagging.*

-   **Tests:** Run the test suite.
    ```bash
    uv run pytest
    ```

**GitHub Release Workflow:** Pushing a version tag (e.g., `v1.0.1`) triggers a GitHub Action (`.github/workflows/release.yml`) to create a GitHub Release and upload the built wheel as an asset.

## License

MIT License

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
