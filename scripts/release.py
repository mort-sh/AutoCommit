from pathlib import Path
import sys

# --- Configuration ---
MAIN_BRANCH = "main"  # Or "master" if that's your default
REMOTE_NAME = "origin"
PYPROJECT_PATH = "pyproject.toml"
SCRIPTS_DIR = "scripts"


def get_scripts_paths():
    """Returns a list of absolute paths for all scripts in the SCRIPTS_DIR."""
    scripts_dir_path = Path(SCRIPTS_DIR).resolve()
    if not scripts_dir_path.is_dir():
        print(f"Error: Scripts directory '{scripts_dir_path}' not found.")
        sys.exit(1)
    # Collect all .py files in the scripts directory
    script_paths = [
        script.resolve() for script in scripts_dir_path.glob("*.py") if script.is_file()
    ]
    return script_paths


def main():
    # Populate SCRIPTS_DIR with a list of absolute paths for relevant scripts
    scripts_paths = get_scripts_paths()

    # TODO:
    # Features I want:
    # - Check if the current branch is the main branch
    #   - If it is, then
    #     - throw an error
    #   - If it is not, then
    #     - Run the tests
    #     - automatically bump the version
    #     - create a new release branch
    #     - commit the changes using `auto-commit.exe`
    #     - push the changes
    #     - create a pull request

    return 0


if __name__ == "__main__":
    sys.exit(main())
