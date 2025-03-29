#!/usr/bin/env python3
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def print_separator(message=""):
    """Print a separator line with an optional message."""
    width = shutil.get_terminal_size().columns - 10
    if message:
        print(f"\n{'-' * 10} {message} {'-' * (width - len(message) - 12)}")
    else:
        print(f"\n{'-' * width}")


def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
        return result.stdout, None
    except subprocess.CalledProcessError as e:
        return None, f"Error: {e.stderr}"


def run_tests():
    """Run all tests and return True if they pass."""
    print_separator("Running Tests")
    stdout, stderr = run_command(["uv", "run", "pytest", "-v"])

    if stderr:
        print(f"Test execution failed:\n{stderr}")
        return False

    if stdout:
        print(stdout)

    print("All tests passed successfully!")
    return True


def create_build_directory():
    """Create or clean the build directory."""
    build_dir = Path("build")
    dist_dir = Path("dist")

    # Create/clean directories
    for directory in [build_dir, dist_dir]:
        if directory.exists():
            print(f"Cleaning {directory} directory...")
            shutil.rmtree(directory)
        directory.mkdir(exist_ok=True)
        print(f"Created {directory} directory")

    return build_dir, dist_dir


def build_wheel_package():
    """Build wheel package using UV build."""
    print_separator("Building Wheel Package")
    stdout, stderr = run_command(["uv", "build"])

    if stderr:
        print(f"Wheel build failed:\n{stderr}")
        return False

    if stdout:
        print(stdout)

    wheel_files = list(Path("dist").glob("*.whl"))
    if wheel_files:
        print(f"Wheel package created successfully: {[str(f) for f in wheel_files]}")
        return True
    else:
        print("Wheel build failed - no output file found")
        return False


def build_windows_executable(dist_dir):
    """Build Windows executable using PyInstaller."""
    if platform.system() != "Windows":
        print("Not running on Windows. Creating Windows executable requires Windows environment.")
        print("Skipping Windows build...")
        return False

    print_separator("Building Windows Executable")
    stdout, stderr = run_command(["uv", "pip", "install", "pyinstaller"])

    if stderr:
        print(f"PyInstaller installation failed:\n{stderr}")
        return False

    stdout, stderr = run_command([
        "uv",
        "run",
        "pyinstaller",
        "--onefile",
        "--name",
        "autocommit",
        "--clean",
        "--paths",
        ".",
        "--hidden-import",
        "autocommit.cli.cli",
        "--hidden-import",
        "autocommit.core",
        "--hidden-import",
        "autocommit.utils",
        "main.py",
    ])

    if stderr:
        print(f"Windows build failed:\n{stderr}")
        return False

    # Copy the executable to the dist directory
    exe_path = Path("dist/autocommit.exe")
    if exe_path.exists():
        print(f"Windows executable created successfully at: {exe_path}")
        return True
    else:
        print("Windows executable build failed - no output file found")
        return False


def build_macos_executable(dist_dir):
    """Build MacOS executable using PyInstaller."""
    if platform.system() != "Darwin":
        print("Not running on MacOS. Creating MacOS executable requires MacOS environment.")
        print("Skipping MacOS build...")
        return False

    print_separator("Building MacOS Executable")
    stdout, stderr = run_command(["uv", "pip", "install", "pyinstaller"])

    if stderr:
        print(f"PyInstaller installation failed:\n{stderr}")
        return False

    stdout, stderr = run_command([
        "uv",
        "run",
        "pyinstaller",
        "--onefile",
        "--name",
        "autocommit",
        "--clean",
        "--paths",
        ".",
        "--hidden-import",
        "autocommit.cli.cli",
        "--hidden-import",
        "autocommit.core",
        "--hidden-import",
        "autocommit.utils",
        "main.py",
    ])

    if stderr:
        print(f"MacOS build failed:\n{stderr}")
        return False

    # Copy the executable to the dist directory
    app_path = Path("dist/autocommit")
    if app_path.exists():
        print(f"MacOS executable created successfully at: {app_path}")
        return True
    else:
        print("MacOS executable build failed - no output file found")
        return False


def verify_build(dist_dir):
    """Verify the build outputs exist."""
    print_separator("Verifying Build Outputs")

    outputs = list(dist_dir.glob("*"))
    if not outputs:
        print("No build outputs found!")
        return False

    print("Build outputs:")
    for output in outputs:
        print(f"  - {output}")

    return True


def main():
    """Main build function."""
    print("AutoCommit Build Script")
    print("==========================")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")

    # Run tests
    if not run_tests():
        print("Tests failed. Aborting build.")
        return 1

    # Create build directory
    build_dir, dist_dir = create_build_directory()

    # Build Python package (wheel)
    print_separator("Building Python Package")
    if not build_wheel_package():
        print("Package build failed.")
        return 1

    # Build platform-specific executables
    current_platform = platform.system()
    if current_platform == "Windows":
        success = build_windows_executable(dist_dir)
    elif current_platform == "Darwin":
        success = build_macos_executable(dist_dir)
    else:
        print(f"Platform {current_platform} is not supported for direct compilation.")
        print(
            "You need to run this script on Windows for Windows builds "
            "or MacOS for MacOS builds."
        )
        success = True  # Don't fail the build on unsupported platforms

    if not success:
        print("Executable build process failed.")
        return 1

    # Verify build
    if not verify_build(dist_dir):
        return 1

    print_separator()
    print("Build completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
