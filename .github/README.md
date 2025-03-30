# GitHub Actions Workflows

This directory contains the GitHub Actions workflows used by the AutoCommit project for continuous integration, publishing, and release management.

## Workflows

Located in the `.github/workflows/` directory:

### `ci.yml` (Continuous Integration)

**Trigger:** Runs on every push to the `main` branch and on every pull request targeting `main`.

**Purpose:**
-   Sets up the Python environment.
-   Installs project dependencies.
-   Runs linters (e.g., Ruff, MyPy) to ensure code quality and style consistency.
-   Executes the test suite (e.g., using `pytest`) to verify functionality.

**Goal:** To ensure that code merged into the main branch is functional, passes tests, and adheres to coding standards.

### `publish.yml` (Publish to PyPI)

**Trigger:** Runs when a new tag matching the pattern `v*.*.*` (e.g., `v1.0.0`) is pushed to the repository.

**Purpose:**
-   Builds the project into distributable formats (source distribution and wheel).
-   Publishes the built packages to the Python Package Index (PyPI).

**Goal:** To automate the distribution of new package versions to PyPI upon tagging a release. Requires appropriate secrets (e.g., `PYPI_API_TOKEN`) to be configured in the repository settings.

### `release.yml` (Create GitHub Release)

**Trigger:** Runs when a new tag matching the pattern `v*.*.*` is pushed to the repository (often triggered after `publish.yml` completes).

**Purpose:**
-   Creates a corresponding GitHub Release based on the pushed tag.
-   Automatically generates release notes based on commit history since the last tag (or uses the tag annotation).
-   May attach build artifacts (like wheels) from the `publish.yml` workflow to the GitHub Release.

**Goal:** To automate the creation of official GitHub Releases, providing users with changelogs and downloadable artifacts for each version.

## Overview

These workflows automate key parts of the development lifecycle:
-   **CI:** Maintains code quality and stability.
-   **Publish:** Distributes the package for users.
-   **Release:** Documents and archives official releases on GitHub.
