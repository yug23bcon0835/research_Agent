#!/usr/bin/env python3
"""Script to check code quality with various linting tools."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def main():
    """Main code quality checker."""
    project_root = Path(__file__).parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    print("Code Quality Checks")
    print("=" * 60)
    
    # Quality check commands
    quality_commands = [
        (["python", "-m", "black", "--check", "app/", "tests/", "main.py"], "Black formatting check"),
        (["python", "-m", "isort", "--check-only", "app/", "tests/", "main.py"], "Import sorting check"),
        (["python", "-m", "flake8", "app/", "tests/", "main.py"], "Flake8 linting"),
        (["python", "-m", "mypy", "app/"], "Type checking with mypy"),
    ]
    
    # Run all quality checks
    all_passed = True
    for cmd, description in quality_commands:
        if not run_command(cmd, description):
            all_passed = False
            print(f"FAILED: {description}")
        else:
            print(f"PASSED: {description}")
    
    print("\n" + "="*60)
    if all_passed:
        print("All code quality checks passed! ✅")
        return 0
    else:
        print("Some code quality checks failed! ❌")
        print("\nTo fix formatting issues, run:")
        print("  python -m black app/ tests/ main.py")
        print("  python -m isort app/ tests/ main.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
