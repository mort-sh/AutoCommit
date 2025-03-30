<span align="center">

# AutoCommit

AI-powered Git commit message generator that automates commit messages using OpenAI's API.

<img src="logo.png" alt="AutoCommit Logo">
</span>

## Features

- Automatically generates meaningful commit messages for changed files
- Handles binary files and deleted files
- Optionally pushes commits after creation
- Customizable OpenAI model selection
- Rich terminal output with color-coded information
- Splits large diffs into semantically meaningful chunks
- Parallel processing for significant performance improvements

## Requirements

- Python 3.12 or higher
- OpenAI API key set in your environment variables
- Git installed and accessible from the command line
- [UV package manager](https://github.com/astral-sh/uv) (recommended)

## Installation

### With UV (recommended)

Install directly from the repository using UV:
```bash
git clone https://github.com/mort-sh/AutomaticGitCommit.git
cd AutomaticGitCommit
uv pip install -e .
```

### With pip

Install directly from the repository using pip:
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

To generate commit messages for all uncommitted changes:

```bash
autocommit
```

### Key Options

```
autocommit [OPTIONS]

Options:
  --test            Test mode, don't actually commit changes
  --push            Push commits after creating them
  --remote REMOTE   Remote repository to push to (default: origin)
  --branch BRANCH   Branch to push to (defaults to current)
  --model MODEL     OpenAI model to use (default: gpt-4o-mini)
  --auto-track      Automatically track all untracked files without prompting
  --debug           Enable debug logging
  --chunk-level {0,1,2,3}  Control commit atomicity:
                         0=coarse (file level)
                         1=standard (balanced)
                         2=fine (logical units, default)
                         3=atomic (single responsibility)
  --parallel N      Control parallelism level:
                         0=auto (based on CPU cores, default)
                         N=specific number of workers
```

### Handling Untracked Files

When AutoCommit detects untracked files, it will interactively prompt you for each file:

```
Untracked file: path/to/file.py
[A]dd file, [I]gnore file (add to .gitignore), [S]kip file, or [AA] Add all untracked files:
```

Options:
- **A**: Add this specific file to the commit
- **I**: Add the file to `.gitignore`
- **S**: Skip this file (won't be committed, won't add to `.gitignore`)
- **AA**: Add all remaining untracked files without further prompting

Use the `--auto-track` option to automatically add all untracked files without prompting.

### Commit Atomicity Levels

AutoCommit provides fine-grained control over commit atomicity using the `--chunk-level` option:

#### Level 0: Coarse (File-level)
- Each modified file produces one commit.
- Useful for large-scale refactorings or config changes where individual file changes are the main unit.

#### Level 1: Standard
- Balances commit size with logical separation.
- Uses git hunks and maximum diff size to determine chunks.

#### Level 2: Fine (Logical Units - Default)
- Separates changes by logical units like classes or methods within files.
- Focuses on the intent of the change rather than just textual proximity.

#### Level 3: Atomic (Single Responsibility)
- Aims to isolate each atomic change (e.g., function signature update, implementation detail, documentation fix) into its own commit.
- Optimizes for precise code review and detailed historical traceability.

### Examples

Test mode (preview without committing):
```bash
autocommit --test
```

Generate commits and push them:
```bash
autocommit --push
```

Use a different OpenAI model:
```bash
autocommit --model gpt-4o
```

Create atomic commits:
```bash
autocommit --chunk-level 3
```

Use maximum parallelism with 8 workers:
```bash
autocommit --parallel 8
```

Enable debug output:
```bash
autocommit --debug
```

## How It Works

1. Scans your Git repository for uncommitted changes
2. Extracts the diff for each changed file
3. Splits changes into appropriate units based on chunk level
4. Sends chunks to OpenAI's API in parallel with specialized prompts
5. Generates conventional commit messages concurrently
6. Commits changes with the AI-generated messages in correct order
7. Optionally pushes to the remote repository

## Development Scripts

AutoCommit comes with utility scripts to help with development and distribution. These scripts use [UV package manager](https://github.com/astral-sh/uv) for enhanced performance and reliability.

### Build Script

The build script creates Python packages and optionally platform-specific executables:

```bash
# Install development dependencies first
uv pip install -e ".[dev]"

# Build Python wheel package only
project_build

# Build Python wheel package and platform-specific executable
project_build --executable
```

The build script will:
1. Run all tests to ensure everything is working
2. Create Python wheel package in the `dist/` directory
3. Optionally create platform-specific executables when `--executable` is passed
   - Windows: `.exe` file in the `dist/` directory
   - macOS: Binary file in the `dist/` directory

### Clean Script

Removes temporary files, build artifacts, and clears UV cache:

```bash
# Clean up build artifacts and cache files
project_clean
```

The clean script will remove:
- Build and dist directories
- Python cache files (`__pycache__`, `.pyc`)
- Test cache (`.pytest_cache`, `.coverage`, `.mypy_cache`)
- Packaging artifacts (`.egg-info`)
- PyInstaller files (`.spec`)
- UV package manager cache

### Running Scripts Manually

You can also run the scripts directly with UV:

```bash
# Run the build script
uv run python -m scripts.build

# Run the clean script
uv run python -m scripts.clean

# Run tests
uv run pytest
```

### Release Script (New)

The release script automates the process of preparing a new release version:

```bash
# Run the release helper script
uv run project_release
```

This script performs the following steps:
1.  Fetches the latest state from the remote `origin/main` branch.
2.  Compares the local commit hash and `pyproject.toml` version against the remote state.
3.  **If** the local commit differs from `origin/main` **and** the local version matches the latest remote tag version, it automatically increments the patch version in `pyproject.toml` (e.g., `1.0.0` -> `1.0.1`).
4.  Runs tests (`uv run pytest`).
5.  Builds the project wheel (`uv build`).
6.  **If the version was bumped:**
    *   Creates a new branch (e.g., `release/v1.0.1`).
    *   Commits the version change in `pyproject.toml` to this branch.
    *   Pushes the new branch to `origin`.
    *   **Attempts** to create a Pull Request on GitHub from the release branch to `main`. (Requires GitHub CLI or API access configured).
    *   Switches back to the `main` branch locally.
    *   Provides instructions to review the PR and, after merging, push the corresponding tag (e.g., `git tag v1.0.1 && git push origin v1.0.1`).
7.  **If no version bump occurred:** It simply runs tests and builds, indicating that manual steps are needed if a release is intended.

**GitHub Release Workflow:** Pushing a version tag (e.g., `v1.0.1`) to the repository will automatically trigger a GitHub Action (`.github/workflows/release.yml`) that:
*   Creates a GitHub Release associated with that tag.
*   Builds the project wheel.
*   Uploads the wheel file as an asset to the GitHub Release.

## License

MIT License

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
