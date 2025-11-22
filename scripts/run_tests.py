#!/usr/bin/env python3
"""Script to run the test suite with coverage reporting."""

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
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with return code: {result.returncode}")
        return False
    
    return True


def main():
    """Main test runner."""
    project_root = Path(__file__).parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    print("Multi-Agent Research App Test Suite")
    print("=" * 60)
    
    # Test commands
    test_commands = [
        (
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            "Run all tests with verbose output"
        ),
        (
            ["python", "-m", "pytest", "tests/test_models.py", "-v"],
            "Run model tests"
        ),
        (
            ["python", "-m", "pytest", "tests/test_agents.py", "-v"],
            "Run agent tests"
        ),
        (
            ["python", "-m", "pytest", "tests/test_orchestrator.py", "-v"],
            "Run orchestrator tests"
        ),
        (
            ["python", "-m", "pytest", "tests/test_integration.py", "-v"],
            "Run integration tests"
        ),
    ]
    
    # Try to run with coverage if available
    try:
        coverage_commands = [
            (
                ["python", "-m", "pytest", "tests/", "--cov=app", "--cov-report=term-missing", "--cov-report=html"],
                "Run tests with coverage reporting"
            )
        ]
        test_commands.extend(coverage_commands)
    except ImportError:
        print("Coverage not available, skipping coverage tests")
    
    # Run all test commands
    all_passed = True
    for cmd, description in test_commands:
        if not run_command(cmd, description):
            all_passed = False
            print(f"FAILED: {description}")
        else:
            print(f"PASSED: {description}")
    
    print("\n" + "="*60)
    if all_passed:
        print("All tests passed! ✅")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())
