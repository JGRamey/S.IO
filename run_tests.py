#!/usr/bin/env python3
"""Test runner script for Yggdrasil project."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type='all', verbose=False, coverage=False):
    """Run tests based on type and options."""
    
    # Base pytest command
    cmd = ['python3', '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=yggdrasil', '--cov-report=html', '--cov-report=term'])
    
    # Add test selection based on type
    if test_type == 'unit':
        cmd.extend(['-m', 'unit'])
        print("🧪 Running unit tests (fast, no dependencies)...")
    elif test_type == 'integration':
        cmd.extend(['-m', 'integration'])
        print("🔗 Running integration tests (requires services)...")
    elif test_type == 'mock':
        cmd.append('tests/test_*mock*.py')
        print("🎭 Running mock tests...")
    elif test_type == 'agents':
        cmd.append('tests/test_*agent*.py')
        print("🤖 Running agent tests...")
    elif test_type == 'config':
        cmd.append('tests/test_config*.py')
        print("⚙️  Running configuration tests...")
    elif test_type == 'utils':
        cmd.append('tests/test_utils*.py')
        print("🛠️  Running utility tests...")
    elif test_type == 'bias':
        cmd.append('tests/test_bias*.py')
        print("🔍 Running bias detection tests...")
    elif test_type == 'quick':
        cmd.extend(['-m', 'unit', '--maxfail=5', '-x'])
        print("⚡ Running quick tests (unit only, fail fast)...")
    elif test_type == 'standalone':
        cmd.extend(['-k', 'standalone'])
        print("🏃 Running standalone tests...")
    elif test_type == 'all':
        print("🚀 Running all tests...")
    else:
        print(f"❌ Unknown test type: {test_type}")
        return False
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(description='Run Yggdrasil tests')
    parser.add_argument(
        'test_type',
        nargs='?',
        default='all',
        choices=['all', 'unit', 'integration', 'mock', 'agents', 'config', 'utils', 'bias', 'quick', 'standalone'],
        help='Type of tests to run'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--list-tests', action='store_true', help='List available tests')
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("📋 Available test types:")
        print("  all        - Run all tests")
        print("  unit       - Fast unit tests (no external dependencies)")
        print("  integration- Integration tests (requires services)")
        print("  mock       - Mock tests (isolated with mocks)")
        print("  agents     - All agent-related tests")
        print("  config     - Configuration tests")
        print("  utils      - Utility function tests")
        print("  bias       - Bias detection tests")
        print("  quick      - Quick unit tests with fail-fast")
        print("  standalone - Standalone tests")
        return
    
    print("🎯 Yggdrasil Test Runner")
    print("=" * 40)
    
    success = run_tests(args.test_type, args.verbose, args.coverage)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
