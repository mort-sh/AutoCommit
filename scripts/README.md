# Utility Scripts

This directory contains utility scripts to help with common development and maintenance tasks for the AutoCommit project. These scripts are designed to be run from the root directory of the project.

## Scripts

### `build.py`

**Purpose:** Builds the project, preparing it for distribution or installation.

**Usage:**
```bash
python scripts/build.py
```
This script typically handles tasks like compiling code (if necessary), packaging assets, and creating distributable artifacts (e.g., wheels, source distributions).

### `clean.py`

**Purpose:** Removes temporary files, build artifacts, and other generated files to provide a clean working directory.

**Usage:**
```bash
python scripts/clean.py
```
Useful for ensuring a fresh build or removing clutter like `__pycache__` directories, build outputs (`dist/`, `build/`), and test caches (`.pytest_cache`).

### `release.py`

**Purpose:** Automates the process of creating a new release.

**Usage:**
```bash
python scripts/release.py --version <new_version>
```
This script likely handles tasks such as:
-   Updating the project version number in relevant files (e.g., `pyproject.toml`).
-   Creating Git tags for the release.
-   Potentially building the project and uploading it to a package index like PyPI (often coordinated with CI/CD).

### `generate_dummy_data.py`

**Purpose:** Creates, modifies, or deletes dummy text files in a `dummy_test_data/` directory to simulate changes for testing purposes (e.g., testing `autocommit.exe`).

**Usage:**
```bash
python scripts/generate_dummy_data.py
```
This script randomly performs one of the following actions:
- Creates a new file (`dummy_file_N.txt`) with random text.
- Modifies an existing dummy file by appending random text.
- Deletes a random existing dummy file.
It manages the `dummy_test_data/` directory automatically.

## Why Use These Scripts?

-   **Consistency:** Ensures common tasks are performed the same way every time.
-   **Automation:** Reduces manual effort and potential for errors.
-   **Clarity:** Centralizes common development workflows.
