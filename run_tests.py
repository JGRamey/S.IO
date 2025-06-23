#!/usr/bin/env python3
"""
Enhanced Test Runner for Yggdrasil/S.IO Project
Comprehensive testing with detailed reporting and logging
"""

import sys
import subprocess
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import os


class YggdrasilTestRunner:
    """Enhanced test runner with comprehensive reporting and logging."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_log_file = self.logs_dir / f"test_report_{timestamp}.log"
        self.latest_report = self.logs_dir / "latest_test_report.json"
        
    def log_message(self, message, also_print=True):
        """Log message to file and optionally print to console."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = f"[{timestamp}] {message}"
        
        with open(self.test_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
        
        if also_print:
            print(message)
    
    def run_test_suite(self, test_type='all', verbose=False, coverage=False, generate_report=True):
        """Run comprehensive test suite with detailed reporting."""
        
        start_time = time.time()
        self.log_message("🎯 YGGDRASIL/S.IO COMPREHENSIVE TEST EXECUTION")
        self.log_message("=" * 80)
        self.log_message(f"Test Type: {test_type}")
        self.log_message(f"Verbose Mode: {verbose}")
        self.log_message(f"Coverage Analysis: {coverage}")
        self.log_message(f"Log File: {self.test_log_file}")
        self.log_message("")
        
        # Build pytest command
        cmd = ['python3', '-m', 'pytest']
        
        # Add output options
        cmd.extend(['--tb=short'])
        
        if verbose:
            cmd.append('-v')
        else:
            cmd.append('-q')
        
        # Add coverage if requested
        if coverage:
            coverage_dir = self.logs_dir / "coverage"
            cmd.extend([
                '--cov=yggdrasil',
                '--cov-report=html:' + str(coverage_dir),
                '--cov-report=term-missing',
                '--cov-report=json:' + str(self.logs_dir / "coverage.json")
            ])
        
        # Test suite configurations
        test_configs = {
            'unit': {
                'args': ['-m', 'unit', 'tests/'],
                'description': '🧪 Unit Tests (fast, no dependencies)',
                'expected_tests': ['test_config_unit.py', 'test_utils_unit.py', 'test_agents_mock.py']
            },
            'integration': {
                'args': ['-m', 'integration', 'tests/'],
                'description': '🔗 Integration Tests (requires services)',
                'expected_tests': ['test_integration.py']
            },
            'mock': {
                'args': ['tests/test_agents_mock.py'],
                'description': '🎭 Mock Tests (isolated testing)',
                'expected_tests': ['test_agents_mock.py']
            },
            'agents': {
                'args': ['tests/test_mcp_agents.py', 'tests/quick_agent_test.py', 'tests/test_agents_mock.py'],
                'description': '🤖 AI Agent Tests',
                'expected_tests': ['test_mcp_agents.py', 'quick_agent_test.py', 'test_agents_mock.py']
            },
            'config': {
                'args': ['tests/test_config_unit.py'],
                'description': '⚙️  Configuration Tests',
                'expected_tests': ['test_config_unit.py']
            },
            'utils': {
                'args': ['tests/test_utils_unit.py'],
                'description': '🛠️  Utility Tests',
                'expected_tests': ['test_utils_unit.py']
            },
            'bias': {
                'args': ['tests/test_bias_standalone.py'],
                'description': '🔍 Bias Detection Tests',
                'expected_tests': ['test_bias_standalone.py']
            },
            'quick': {
                'args': ['tests/test_config_unit.py', 'tests/test_utils_unit.py', 'tests/test_agents_mock.py', '--maxfail=5', '-x'],
                'description': '⚡ Quick Tests (fail fast)',
                'expected_tests': ['test_config_unit.py', 'test_utils_unit.py']
            },
            'standalone': {
                'args': ['tests/test_bias_standalone.py'],
                'description': '🏃 Standalone Tests',
                'expected_tests': ['test_bias_standalone.py']
            },
            'all': {
                'args': ['tests/', '--ignore=tests/conftest.py'],
                'description': '🚀 Complete Test Suite (all tests)',
                'expected_tests': 'all'
            }
        }
        
        # Get test configuration
        if test_type not in test_configs:
            self.log_message(f"❌ Unknown test type: {test_type}")
            return False
        
        config = test_configs[test_type]
        cmd.extend(config['args'])
        
        self.log_message(config['description'])
        self.log_message(f"Command: {' '.join(cmd)}")
        self.log_message("")
        
        # Run tests
        try:
            self.log_message("🔄 Executing tests...")
            
            # Capture output for logging
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Log test output
            self.log_message("📊 TEST OUTPUT:")
            self.log_message("-" * 40)
            if result.stdout:
                self.log_message(result.stdout, also_print=verbose)
            if result.stderr:
                self.log_message("STDERR:", also_print=True)
                self.log_message(result.stderr, also_print=True)
            
            # Calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Determine success/failure
            success = result.returncode == 0
            
            # Generate summary
            self.log_message("")
            self.log_message("📈 TEST EXECUTION SUMMARY:")
            self.log_message("=" * 40)
            self.log_message(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
            self.log_message(f"Return Code: {result.returncode}")
            self.log_message(f"Execution Time: {execution_time:.2f} seconds")
            self.log_message(f"Test Type: {test_type}")
            self.log_message(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
            
            # Parse test results for detailed reporting
            test_stats = self._parse_test_output(result.stdout)
            
            if test_stats:
                self.log_message(f"Tests Collected: {test_stats.get('collected', 'N/A')}")
                self.log_message(f"Tests Passed: {test_stats.get('passed', 'N/A')}")
                self.log_message(f"Tests Failed: {test_stats.get('failed', 'N/A')}")
                self.log_message(f"Tests Skipped: {test_stats.get('skipped', 'N/A')}")
                self.log_message(f"Warnings: {test_stats.get('warnings', 'N/A')}")
            
            # Generate JSON report if requested
            if generate_report:
                self._generate_json_report(test_type, success, execution_time, test_stats, result)
            
            # Print summary to console
            print("\n" + "=" * 50)
            print(f"🎯 TEST SUMMARY: {test_type.upper()}")
            print("=" * 50)
            print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
            print(f"Time: {execution_time:.2f}s")
            if test_stats:
                print(f"Results: {test_stats.get('passed', 0)} passed, {test_stats.get('failed', 0)} failed")
            print(f"Report: {self.test_log_file}")
            print("=" * 50)
            
            return success
            
        except subprocess.TimeoutExpired:
            self.log_message("❌ Test execution timed out (5 minutes)")
            return False
        except Exception as e:
            self.log_message(f"❌ Error running tests: {e}")
            return False
    
    def _parse_test_output(self, output):
        """Parse pytest output to extract test statistics."""
        stats = {}
        
        if not output:
            return stats
        
        lines = output.split('\n')
        
        # Look for test collection line
        for line in lines:
            if 'collected' in line and 'item' in line:
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'collected' in part and i > 0:
                            stats['collected'] = int(parts[i-1])
                            break
                except (ValueError, IndexError):
                    pass
        
        # Look for final results line
        for line in reversed(lines):
            if 'passed' in line or 'failed' in line or 'error' in line:
                # Parse lines like "5 passed, 29 warnings in 0.02s"
                try:
                    if 'passed' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'passed' in part and i > 0:
                                stats['passed'] = int(parts[i-1])
                            elif 'failed' in part and i > 0:
                                stats['failed'] = int(parts[i-1])
                            elif 'skipped' in part and i > 0:
                                stats['skipped'] = int(parts[i-1])
                            elif 'warnings' in part and i > 0:
                                stats['warnings'] = int(parts[i-1])
                except (ValueError, IndexError):
                    pass
                break
        
        return stats
    
    def _generate_json_report(self, test_type, success, execution_time, test_stats, result):
        """Generate a detailed JSON report for analysis and tracking."""
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_type": test_type,
            "success": success,
            "execution_time_seconds": round(execution_time, 2),
            "return_code": result.returncode,
            "statistics": test_stats,
            "command": result.args if hasattr(result, 'args') else [],
            "log_file": str(self.test_log_file),
            "project_root": str(self.project_root),
            "python_version": sys.version,
            "environment": {
                "platform": sys.platform,
                "cwd": str(Path.cwd())
            }
        }
        
        # Add coverage info if available
        coverage_file = self.logs_dir / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    report["coverage"] = {
                        "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                        "files_covered": len(coverage_data.get("files", {}))
                    }
            except Exception:
                pass
        
        # Save the report
        with open(self.latest_report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_message(f"📋 JSON Report saved: {self.latest_report}")
    
    def list_available_tests(self):
        """List all available test types and discovered test files."""
        
        print("📋 YGGDRASIL TEST SUITE OVERVIEW")
        print("=" * 50)
        
        # Discover actual test files
        tests_dir = self.project_root / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        
        print(f"\n🔍 Discovered Test Files ({len(test_files)}):")
        for test_file in sorted(test_files):
            print(f"  📄 {test_file.name}")
        
        print(f"\n🎯 Available Test Types:")
        test_types = {
            'all': 'Run complete test suite (recommended)',
            'unit': 'Fast unit tests (no external dependencies)',
            'integration': 'Integration tests (requires services)',
            'mock': 'Mock tests (isolated with mocks)',
            'agents': 'All AI agent-related tests',
            'config': 'Configuration management tests',
            'utils': 'Utility function tests',
            'bias': 'Bias detection system tests',
            'quick': 'Quick validation tests (fail fast)',
            'standalone': 'Standalone tests (no dependencies)'
        }
        
        for test_type, description in test_types.items():
            print(f"  {test_type:12} - {description}")
        
        print(f"\n💡 Usage Examples:")
        print(f"  python3 run_tests.py all --coverage     # Complete suite with coverage")
        print(f"  python3 run_tests.py quick -v           # Quick tests with verbose output")
        print(f"  python3 run_tests.py unit                # Fast unit tests only")
        print(f"  python3 run_tests.py --list-tests       # Show this help")


def main():
    """Enhanced main function with comprehensive options."""
    
    parser = argparse.ArgumentParser(
        description='Enhanced Yggdrasil/S.IO Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_tests.py all --coverage     # Run all tests with coverage analysis
  python3 run_tests.py quick -v           # Quick tests with verbose output
  python3 run_tests.py agents             # Test AI agent functionality
  python3 run_tests.py --list-tests       # Show available tests
        """
    )
    
    parser.add_argument(
        'test_type',
        nargs='?',
        default='all',
        choices=['all', 'unit', 'integration', 'mock', 'agents', 'config', 'utils', 'bias', 'quick', 'standalone'],
        help='Type of tests to run (default: all)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (show detailed test results)'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='Generate code coverage analysis'
    )
    
    parser.add_argument(
        '--list-tests',
        action='store_true',
        help='List available test types and discovered test files'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip JSON report generation'
    )
    
    args = parser.parse_args()
    
    # Create test runner instance
    runner = YggdrasilTestRunner()
    
    if args.list_tests:
        runner.list_available_tests()
        return
    
    # Run the test suite
    print("🚀 Starting Yggdrasil/S.IO Test Suite...")
    print("=" * 60)
    
    success = runner.run_test_suite(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        generate_report=not args.no_report
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
