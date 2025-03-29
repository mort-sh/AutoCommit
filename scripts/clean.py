#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys


def print_separator(message=""):
    """Print a separator line with an optional message."""
    width = 80
    if message:
        print(f"\n{'-' * 10} {message} {'-' * (width - len(message) - 12)}")
    else:
        print(f"\n{'-' * width}")


def remove_directory(path):
    """Remove a directory if it exists."""
    if path.exists():
        try:
            print(f"Removing directory: {path}")
            shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error removing {path}: {e}")
            return False
    return False


def remove_file(path):
    """Remove a file if it exists."""
    if path.exists():
        try:
            print(f"Removing file: {path}")
            path.unlink()
            return True
        except Exception as e:
            print(f"Error removing {path}: {e}")
            return False
    return False


def find_and_remove_pycache(root_dir):
    """Find and remove all __pycache__ directories."""
    pycache_dirs = list(root_dir.glob("**/__pycache__"))
    print(f"Found {len(pycache_dirs)} __pycache__ directories")

    removed = 0
    for dir_path in pycache_dirs:
        if remove_directory(dir_path):
            removed += 1

    return removed


def find_and_remove_pyc_files(root_dir):
    """Find and remove all .pyc files."""
    pyc_files = list(root_dir.glob("**/*.pyc"))
    print(f"Found {len(pyc_files)} .pyc files")

    removed = 0
    for file_path in pyc_files:
        if remove_file(file_path):
            removed += 1

    return removed


def find_and_remove_pytest_cache(root_dir):
    """Find and remove all pytest cache files and directories."""
    # Remove .pytest_cache directories
    pytest_cache_dirs = list(root_dir.glob("**/.pytest_cache"))
    print(f"Found {len(pytest_cache_dirs)} .pytest_cache directories")

    removed = 0
    for dir_path in pytest_cache_dirs:
        if remove_directory(dir_path):
            removed += 1

    return removed


def find_and_remove_mypy_cache(root_dir):
    """Find and remove all mypy cache files and directories."""
    mypy_cache_dirs = list(root_dir.glob("**/.mypy_cache"))
    print(f"Found {len(mypy_cache_dirs)} .mypy_cache directories")

    removed = 0
    for dir_path in mypy_cache_dirs:
        if remove_directory(dir_path):
            removed += 1

    return removed


def find_and_remove_coverage_files(root_dir):
    """Find and remove coverage files."""
    coverage_files = list(root_dir.glob(".coverage")) + list(root_dir.glob(".coverage.*"))
    htmlcov_dir = root_dir / "htmlcov"

    removed = 0
    print(f"Found {len(coverage_files)} coverage files")
    for file_path in coverage_files:
        if remove_file(file_path):
            removed += 1

    if htmlcov_dir.exists():
        print("Found htmlcov directory")
        if remove_directory(htmlcov_dir):
            removed += 1

    return removed


def remove_egg_info(root_dir):
    """Find and remove all .egg-info directories."""
    egg_info_dirs = list(root_dir.glob("**/*.egg-info"))
    print(f"Found {len(egg_info_dirs)} .egg-info directories")

    removed = 0
    for dir_path in egg_info_dirs:
        if remove_directory(dir_path):
            removed += 1

    return removed


def clean_build_directories(root_dir):
    """Remove build and dist directories."""
    build_dir = root_dir / "build"
    dist_dir = root_dir / "dist"

    removed = 0
    if remove_directory(build_dir):
        removed += 1

    if remove_directory(dist_dir):
        removed += 1

    return removed


def run_command(command):
    """Run a command and return the result."""
    try:
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout, None
    except subprocess.CalledProcessError as e:
        return None, f"Error: {e.stderr}"


def run_uv_clean():
    """Run UV cache clean command."""
    print_separator("Cleaning UV Cache")
    stdout, stderr = run_command(["uv", "cache", "clean", "--all"])

    if stderr:
        print(f"UV cache clean failed:\n{stderr}")
        return False

    if stdout:
        print(stdout)

    return True


def main():
    """Main clean function."""
    print("AutoCommit Clean Script")
    print("==========================")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    root_dir = Path(".")

    print_separator("Cleaning Build Directories")
    clean_build_directories(root_dir)

    print_separator("Cleaning Python Cache Files")
    find_and_remove_pycache(root_dir)
    find_and_remove_pyc_files(root_dir)

    print_separator("Cleaning Test Cache Files")
    find_and_remove_pytest_cache(root_dir)
    find_and_remove_mypy_cache(root_dir)
    find_and_remove_coverage_files(root_dir)

    print_separator("Cleaning Package Build Files")
    remove_egg_info(root_dir)

    # Remove PyInstaller build files
    print_separator("Cleaning PyInstaller Files")
    spec_files = list(root_dir.glob("*.spec"))
    print(f"Found {len(spec_files)} .spec files")
    for file_path in spec_files:
        remove_file(file_path)

    # Clean UV cache
    run_uv_clean()

    print_separator()
    print("Cleanup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
