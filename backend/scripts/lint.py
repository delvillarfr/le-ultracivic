#!/usr/bin/env python3
"""
Code linting script for Ultra Civic backend.
Runs Ruff linter with project configuration.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle output."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Run linting checks."""
    project_root = Path(__file__).parent.parent

    print("🚀 Running Ultra Civic Backend Linting")
    print("=" * 50)

    # Change to project directory
    import os

    os.chdir(project_root)

    success = True

    # Run Ruff linting
    if not run_command("ruff check app/ tests/ scripts/", "Ruff linting"):
        success = False

    # Run Ruff import sorting check
    if not run_command(
        "ruff check --select I app/ tests/ scripts/", "Import sorting check"
    ):
        success = False

    # Run type checking with mypy if available
    try:
        subprocess.run(["mypy", "--version"], check=True, capture_output=True)
        if not run_command("mypy app/ --ignore-missing-imports", "Type checking"):
            success = False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  MyPy not available, skipping type checking")

    print("=" * 50)
    if success:
        print("🎉 All linting checks passed!")
        sys.exit(0)
    else:
        print("💥 Some linting checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
