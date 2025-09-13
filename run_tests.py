#!/usr/bin/env python3
"""
Test runner script for Aython project.
Provides different test configurations and options.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} completed successfully")
        return True


def main():
    parser = argparse.ArgumentParser(description="Run Aython tests")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "all", "quick"],
        default="quick",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Include Docker tests"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Include API tests (requires API keys)"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=aython", "--cov-report=html", "--cov-report=xml"])
    
    if args.parallel:
        base_cmd.extend(["-n", "auto"])
    
    # Test selection based on type
    if args.type == "unit":
        cmd = base_cmd + ["tests/test_aython.py", "-m", "not (docker or e2e or integration)"]
        description = "Unit Tests"
        
    elif args.type == "integration":
        cmd = base_cmd + ["tests/test_docker_integration.py", "-m", "not e2e"]
        description = "Integration Tests"
        
    elif args.type == "e2e":
        cmd = base_cmd + ["tests/test_e2e.py", "-m", "e2e"]
        description = "End-to-End Tests"
        
    elif args.type == "all":
        cmd = base_cmd + ["tests/"]
        if not args.docker:
            cmd.extend(["-m", "not docker"])
        if not args.api:
            cmd.extend(["-m", "not api"])
        description = "All Tests"
        
    elif args.type == "quick":
        cmd = base_cmd + ["tests/test_aython.py", "-m", "not (docker or e2e or integration or slow)"]
        description = "Quick Tests"
    
    # Note: timeout would require pytest-timeout plugin
    # cmd.extend(["--timeout=300"])
    
    # Run the tests
    success = run_command(cmd, description)
    
    if success and args.coverage:
        print(f"\n📊 Coverage report generated:")
        print(f"   HTML: htmlcov/index.html")
        print(f"   XML:  coverage.xml")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
