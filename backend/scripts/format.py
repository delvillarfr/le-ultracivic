#!/usr/bin/env python3
"""
Code formatting script for Ultra Civic backend.
Runs Black formatter and Ruff fixes with project configuration.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle output."""
    print(f"🔧 {description}...")
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
    """Run code formatting."""
    project_root = Path(__file__).parent.parent

    print("🎨 Running Ultra Civic Backend Code Formatting")
    print("=" * 50)

    # Change to project directory
    import os

    os.chdir(project_root)

    success = True

    # Run Black formatting
    if not run_command("black app/ tests/ scripts/", "Black code formatting"):
        success = False

    # Run Ruff auto-fixes
    if not run_command("ruff check --fix app/ tests/ scripts/", "Ruff auto-fixes"):
        success = False

    # Run Ruff formatting (alternative to Black)
    if not run_command("ruff format app/ tests/ scripts/", "Ruff formatting"):
        success = False

    print("=" * 50)
    if success:
        print("🎉 Code formatting completed successfully!")
        print("💡 Remember to review changes before committing")
        sys.exit(0)
    else:
        print("💥 Some formatting operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
