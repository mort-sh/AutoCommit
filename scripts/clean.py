#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys

from rich.console import Console
import toml

# ===== Project Configuration =====
# These lists define patterns for project-specific cleaning.
# Consider loading these from pyproject.toml ([tool.scripts.clean])
# or another configuration file for better project isolation.
ADDITIONAL_DIRS_TO_CLEAN = [
    "dummy_test_data"
]  # Directories to clean in addition to standard Python artifacts
ADDITIONAL_FILES_TO_CLEAN = []  # e.g., ["*.log", "*.tmp"]
# ================================

# UV clean command configuration
UV_CLEAN_COMMAND = ["uv", "cache", "clean"]

console = Console()


def get_project_name(toml_file_path: str = "pyproject.toml") -> str | None:
    """
    Reads the pyproject.toml file and returns the project name.

    Args:
        toml_file_path (str): The path to the pyproject.toml file. Defaults to "pyproject.toml".

    Returns:
        str | None: The project name, or None if it cannot be found.
    """
    try:
        with open(toml_file_path, encoding="utf-8") as f:
            data = toml.load(f)
            # Navigate through potential structures [tool.poetry.name] or [project.name]
            if "project" in data and "name" in data["project"]:
                return data["project"]["name"]
            elif "tool" in data and "poetry" in data["tool"] and "name" in data["tool"]["poetry"]:
                return data["tool"]["poetry"]["name"]
            else:
                console.print(
                    "[red]Error: Could not find project name in pyproject.toml under [project.name] or [tool.poetry.name][/red]"
                )
                return None
    except FileNotFoundError:
        console.print(f"[red]Error: {toml_file_path} not found.[/red]")
        return None
    except (KeyError, toml.TomlDecodeError) as e:
        console.print(f"[red]Error reading {toml_file_path}: {e}[/red]")
        return None


def print_separator(message=""):
    """Print a separator line with an optional message."""
    try:
        width = shutil.get_terminal_size().columns - 10
    except OSError:  # Fallback if terminal size cannot be determined
        width = 70
    if message:
        console.print(
            f"\n[bold cyan]{'-' * 10} {message} {'-' * max(0, width - len(message) - 12)}[/bold cyan]"
        )
    else:
        console.print(f"\n[bold cyan]{'-' * max(10, width)}[/bold cyan]")


def remove_directory(path: Path):
    """Remove a directory if it exists."""
    if path.is_dir():  # Ensure it's actually a directory
        try:
            console.print(f"[green]Removing directory: {path}[/green]")
            shutil.rmtree(path)
            return True
        except OSError as e:  # Catch specific OS errors
            console.print(f"[red]Error removing directory {path}: {e}[/red]")
            return False
    elif path.exists():
        console.print(
            f"[yellow]Warning: Expected directory but found file: {path}. Skipping removal.[/yellow]"
        )
        return False
    # If it doesn't exist, it's technically "removed" or clean.
    # console.print(f"Directory not found (already clean): {path}")
    return False  # Return False as no action was taken


def remove_file(path: Path):
    """Remove a file if it exists."""
    if path.is_file():  # Ensure it's actually a file
        try:
            console.print(f"[green]Removing file: {path}[/green]")
            path.unlink()
            return True
        except OSError as e:  # Catch specific OS errors
            console.print(f"[red]Error removing file {path}: {e}[/red]")
            return False
    elif path.exists():
        console.print(
            f"[yellow]Warning: Expected file but found directory: {path}. Skipping removal.[/yellow]"
        )
        return False
    # If it doesn't exist, it's technically "removed" or clean.
    # console.print(f"File not found (already clean): {path}")
    return False  # Return False as no action was taken


def find_and_remove_patterns(root_dir: Path, patterns: list[str], remove_func):
    """Find and remove files/directories matching given glob patterns."""
    removed_count = 0
    for pattern in patterns:
        try:
            matches = list(root_dir.glob(pattern))
            if matches:
                console.print(
                    f"[blue]Found {len(matches)} items matching pattern: '{pattern}'[/blue]"
                )
                for item_path in matches:
                    if remove_func(item_path):
                        removed_count += 1
            # else:
            #     console.print(f"No items found matching pattern: '{pattern}'")
        except Exception as e:
            console.print(f"[red]Error processing pattern '{pattern}': {e}[/red]")
    return removed_count


def clean_standard_artifacts(root_dir: Path):
    """Clean common Python build/cache artifacts."""
    total_removed = 0
    print_separator("Cleaning Standard Python Artifacts")

    # __pycache__ directories
    total_removed += find_and_remove_patterns(root_dir, ["**/__pycache__"], remove_directory)
    # .pyc files
    total_removed += find_and_remove_patterns(root_dir, ["**/*.pyc"], remove_file)
    # .pytest_cache directories
    total_removed += find_and_remove_patterns(root_dir, ["**/.pytest_cache"], remove_directory)
    # .mypy_cache directories
    total_removed += find_and_remove_patterns(root_dir, ["**/.mypy_cache"], remove_directory)
    # coverage files and directories
    total_removed += find_and_remove_patterns(root_dir, [".coverage", ".coverage.*"], remove_file)
    total_removed += find_and_remove_patterns(root_dir, ["htmlcov"], remove_directory)
    # .egg-info directories
    total_removed += find_and_remove_patterns(root_dir, ["**/*.egg-info"], remove_directory)
    # build/dist directories
    total_removed += find_and_remove_patterns(root_dir, ["build", "dist"], remove_directory)
    # PyInstaller .spec files
    total_removed += find_and_remove_patterns(root_dir, ["*.spec"], remove_file)

    console.print(f"[bold green]Removed {total_removed} standard artifact items.[/bold green]")
    return total_removed


def run_command(command):
    """Run a command and return the result."""
    try:
        console.print(f"[blue]Executing: {' '.join(command)}[/blue]")
        # Use encoding for cross-platform compatibility
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        if result.stdout and result.stdout.strip():
            console.print(result.stdout.strip())
        return result.stdout, None
    except subprocess.CalledProcessError as e:
        error_message = f"[red]Command failed with exit code {e.returncode}[/red]"
        if e.stdout and e.stdout.strip():
            error_message += f"\n[red]STDOUT:\n{e.stdout.strip()}[/red]"
        if e.stderr and e.stderr.strip():
            error_message += f"\n[red]STDERR:\n{e.stderr.strip()}[/red]"
        return None, error_message
    except FileNotFoundError:
        return (
            None,
            f"[red]Error: Command not found - ensure '{command[0]}' is installed and in PATH.[/red]",
        )
    except Exception as e:
        return None, f"[red]An unexpected error occurred: {e}[/red]"


def run_uv_clean():
    """Run UV cache clean command."""
    print_separator("Cleaning UV Cache")
    stdout, stderr = run_command(UV_CLEAN_COMMAND)

    if stderr:
        console.print(f"[red]UV cache clean failed:\n{stderr}[/red]")
        return False

    console.print("[bold green]UV cache cleaned successfully.[/bold green]")
    return True


def clean_additional_items(root_dir: Path):
    """Clean additional project-specific files and directories."""
    total_removed = 0
    if not ADDITIONAL_DIRS_TO_CLEAN and not ADDITIONAL_FILES_TO_CLEAN:
        console.print(
            "[yellow]No additional project-specific items configured for cleaning.[/yellow]"
        )
        return 0

    print_separator("Cleaning Additional Project Items")
    if ADDITIONAL_DIRS_TO_CLEAN:
        console.print(f"[blue]Cleaning additional directories: {ADDITIONAL_DIRS_TO_CLEAN}[/blue]")
        # Use find_and_remove_patterns for consistency
        total_removed += find_and_remove_patterns(
            root_dir, ADDITIONAL_DIRS_TO_CLEAN, remove_directory
        )

    if ADDITIONAL_FILES_TO_CLEAN:
        console.print(
            f"[blue]Cleaning additional files/patterns: {ADDITIONAL_FILES_TO_CLEAN}[/blue]"
        )
        # Use find_and_remove_patterns for consistency
        total_removed += find_and_remove_patterns(root_dir, ADDITIONAL_FILES_TO_CLEAN, remove_file)

    console.print(f"[bold green]Removed {total_removed} additional project items.[/bold green]")
    return total_removed


def main():
    """Main clean function."""
    console.print("[bold magenta]Generic Python Project Clean Script[/bold magenta]")
    console.print("[bold magenta]===================================[/bold magenta]")

    # --- Determine Project Root ---
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    console.print(f"[blue]Working directory set to: {os.getcwd()}[/blue]")
    root_dir = Path(".")  # Use relative path from the changed directory

    # --- Get Project Name (Optional for clean, but good practice) ---
    project_name = get_project_name()
    if project_name:
        console.print(f"[bold green]Cleaning project: {project_name}[/bold green]")
    else:
        console.print(
            "[yellow]Warning: Could not determine project name from pyproject.toml.[/yellow]"
        )
        # Decide if this should be a fatal error for clean script
        # return 1

    # --- Clean Standard Artifacts ---
    clean_standard_artifacts(root_dir)

    # --- Clean Additional Project-Specific Items ---
    clean_additional_items(root_dir)

    # --- Clean UV Cache ---
    run_uv_clean()

    print_separator()
    console.print("[bold green]Cleanup completed successfully![/bold green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
