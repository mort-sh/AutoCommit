#!/usr/bin/env python3
"""
Test suite for simulating the Git commit lock issue.
"""

import concurrent.futures
from pathlib import Path
import subprocess
import tempfile
import time

import pytest  # Assuming pytest is used based on pyproject.toml

# --- Test Setup ---


def run_git_command_direct(command: list[str], cwd: Path) -> tuple[int, str, str]:
    """Runs a git command directly, returning return code, stdout, stderr."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout.strip(), stderr.strip()
    except Exception as e:
        return -1, "", f"Error executing git command: {e}"


@pytest.fixture(scope="function")
def temp_git_repo():
    """Creates a temporary Git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        print(f"\nCreating temporary repo at: {repo_path}")

        # Initialize Git repo
        ret, _, err = run_git_command_direct(["git", "init"], cwd=repo_path)
        assert ret == 0, f"Failed to git init: {err}"

        # Basic Git config (needed for commits)
        run_git_command_direct(["git", "config", "user.email", "test@example.com"], cwd=repo_path)
        run_git_command_direct(["git", "config", "user.name", "Test User"], cwd=repo_path)

        # Create an initial commit so HEAD exists
        (repo_path / "initial.txt").write_text("Initial content", encoding="utf-8")
        ret, _, err = run_git_command_direct(["git", "add", "initial.txt"], cwd=repo_path)
        assert ret == 0, f"Failed to git add initial: {err}"
        ret, _, err = run_git_command_direct(
            ["git", "commit", "-m", "Initial commit"], cwd=repo_path
        )
        assert ret == 0, f"Failed to git commit initial: {err}"

        yield repo_path  # Provide the repo path to the test

        # Cleanup happens automatically when exiting the 'with' block


# --- Test Function ---


def commit_single_file_old_style(
    repo_path: Path, file_name: str, content: str
) -> tuple[int, str, str]:
    """Simulates the old commit style: add then commit for a single file."""
    file_path = repo_path / file_name
    file_path.write_text(content, encoding="utf-8")

    # Stage the file
    ret_add, _, err_add = run_git_command_direct(["git", "add", file_name], cwd=repo_path)
    if ret_add != 0:
        print(f"Error staging {file_name}: {err_add}")
        # Return add error if staging fails
        return ret_add, "", err_add

    # Short delay to increase chance of collision
    time.sleep(0.05)

    # Attempt to commit
    commit_msg = f"Commit {file_name}"
    ret_commit, out_commit, err_commit = run_git_command_direct(
        ["git", "commit", "-m", commit_msg], cwd=repo_path
    )
    # Return commit results (including potential lock error)
    return ret_commit, out_commit, err_commit


def test_git_commit_lock_simulation(temp_git_repo):
    """
    Simulates concurrent commits to trigger the index.lock error.
    This test verifies the *problem* existed with the old commit-per-file approach.
    """
    repo_path = temp_git_repo
    num_files = 5  # Number of concurrent commits to attempt
    files_to_commit = [f"file_{i}.txt" for i in range(num_files)]

    results = {}
    lock_errors_found = 0

    print(f"Attempting {num_files} concurrent commits in {repo_path}...")

    # Use ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_files) as executor:
        future_to_file = {
            executor.submit(
                commit_single_file_old_style, repo_path, file_name, f"Content for {file_name}"
            ): file_name
            for file_name in files_to_commit
        }

        for future in concurrent.futures.as_completed(future_to_file):
            file_name = future_to_file[future]
            try:
                ret_code, stdout, stderr = future.result()
                results[file_name] = {"ret": ret_code, "stdout": stdout, "stderr": stderr}
                print(f"Result for {file_name}: ret={ret_code}, stderr='{stderr[:50]}...'")
                # Check specifically for the lock file error
                if "fatal: Unable to create" in stderr and "index.lock': File exists" in stderr:
                    lock_errors_found += 1
            except Exception as exc:
                print(f"{file_name} generated an exception: {exc}")
                results[file_name] = {"ret": -1, "stdout": "", "stderr": str(exc)}

    print(f"\nConcurrent commit simulation finished. Lock errors found: {lock_errors_found}")

    # Assertion: We expect at least one lock error to occur with this simulation
    # Note: This test might be flaky depending on timing and system load.
    # It aims to demonstrate the *potential* for the lock issue, not guarantee it every run.
    assert lock_errors_found > 0, (
        f"Expected at least one index.lock error, but found {lock_errors_found}. Results: {results}"
    )
