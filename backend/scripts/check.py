#!/usr/bin/env python3
"""
Comprehensive code quality check script for Ultra Civic backend.
Runs all quality checks including linting, formatting, security, and tests.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, required=True):
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
        if required:
            print(f"❌ {description} failed:")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        else:
            print(f"⚠️  {description} failed (optional):")
            if e.stderr:
                print(e.stderr)
            return True


def check_tool_availability(tool_name, install_cmd=None):
    """Check if a tool is available."""
    try:
        subprocess.run([tool_name, "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        if install_cmd:
            print(f"⚠️  {tool_name} not available. Install with: {install_cmd}")
        else:
            print(f"⚠️  {tool_name} not available")
        return False


def main():
    """Run comprehensive code quality checks."""
    project_root = Path(__file__).parent.parent

    print("🔬 Running Ultra Civic Backend Quality Checks")
    print("=" * 60)

    # Change to project directory
    import os

    os.chdir(project_root)

    success = True

    # 1. Code formatting check
    print("\n📋 Code Formatting Checks")
    print("-" * 30)
    if not run_command(
        "black --check --diff app/ tests/ scripts/", "Black formatting check"
    ):
        success = False
        print("💡 Run 'python scripts/format.py' to fix formatting issues")

    # 2. Linting checks
    print("\n🔍 Linting Checks")
    print("-" * 20)
    if not run_command("ruff check app/ tests/ scripts/", "Ruff linting"):
        success = False
        print("💡 Run 'ruff check --fix' to auto-fix some issues")

    # 3. Import sorting
    if not run_command("ruff check --select I app/ tests/ scripts/", "Import sorting"):
        success = False

    # 4. Security scanning
    print("\n🔒 Security Scanning")
    print("-" * 20)
    if check_tool_availability("bandit"):
        if not run_command(
            "bandit -r app/ -f json -o bandit-report.json", "Security scan (Bandit)"
        ):
            success = False

    # 5. Type checking (optional)
    print("\n🎯 Type Checking")
    print("-" * 17)
    if check_tool_availability("mypy", "pip install mypy"):
        run_command(
            "mypy app/ --ignore-missing-imports", "Type checking (MyPy)", required=False
        )

    # 6. Test suite
    print("\n🧪 Test Suite")
    print("-" * 12)
    if not run_command("pytest tests/ -v", "Running tests"):
        success = False

    # 7. Configuration validation
    print("\n⚙️  Configuration Validation")
    print("-" * 30)
    run_command(
        "python -c 'from app.config import settings; print(\"✅ Configuration valid\")'",
        "Environment configuration",
        required=False,
    )

    # 8. Database schema validation
    print("\n🗄️  Database Schema")
    print("-" * 18)
    run_command("alembic check", "Alembic migrations check", required=False)

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL QUALITY CHECKS PASSED!")
        print("🚀 Code is ready for commit/deployment")
        sys.exit(0)
    else:
        print("💥 SOME QUALITY CHECKS FAILED!")
        print("🔧 Please fix the issues above before committing")
        sys.exit(1)


if __name__ == "__main__":
    main()
