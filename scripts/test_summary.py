#!/usr/bin/env python3
"""
Test Summary and Analysis Tool for Yggdrasil/S.IO Project
Analyzes test reports and provides insights for project improvement
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse


def load_latest_report(project_root):
    """Load the latest test report."""
    report_file = project_root / "logs" / "latest_test_report.json"
    
    if not report_file.exists():
        print("❌ No test report found. Run tests first with 'python3 run_tests.py'")
        return None
    
    try:
        with open(report_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading test report: {e}")
        return None


def print_test_summary(report):
    """Print a comprehensive test summary."""
    
    print("🎯 YGGDRASIL/S.IO TEST ANALYSIS REPORT")
    print("=" * 60)
    
    # Basic information
    timestamp = datetime.fromisoformat(report['timestamp'].replace('Z', '+00:00'))
    print(f"📅 Report Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🎯 Test Type: {report['test_type'].title()}")
    print(f"⏱️  Execution Time: {report['execution_time_seconds']}s")
    print(f"🔄 Status: {'✅ SUCCESS' if report['success'] else '❌ FAILED'}")
    print()
    
    # Test statistics
    stats = report.get('statistics', {})
    print("📊 TEST STATISTICS:")
    print("-" * 30)
    
    total_tests = stats.get('passed', 0) + stats.get('failed', 0) + stats.get('skipped', 0)
    
    if total_tests > 0:
        success_rate = (stats.get('passed', 0) / total_tests) * 100
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {stats.get('passed', 0)} ({stats.get('passed', 0)/total_tests*100:.1f}%)")
        print(f"❌ Failed: {stats.get('failed', 0)} ({stats.get('failed', 0)/total_tests*100:.1f}%)")
        print(f"⏭️  Skipped: {stats.get('skipped', 0)}")
        print(f"⚠️  Warnings: {stats.get('warnings', 0)}")
        print(f"🏆 Success Rate: {success_rate:.1f}%")
    else:
        print("No test statistics available")
    
    print()
    
    # Coverage analysis
    coverage = report.get('coverage')
    if coverage:
        print("📈 CODE COVERAGE ANALYSIS:")
        print("-" * 30)
        print(f"Total Coverage: {coverage['total_coverage']:.1f}%")
        print(f"Files Analyzed: {coverage['files_covered']}")
        
        # Coverage assessment
        coverage_percent = coverage['total_coverage']
        if coverage_percent >= 80:
            coverage_status = "🟢 Excellent"
        elif coverage_percent >= 60:
            coverage_status = "🟡 Good"
        elif coverage_percent >= 40:
            coverage_status = "🟠 Fair"
        else:
            coverage_status = "🔴 Needs Improvement"
        
        print(f"Assessment: {coverage_status}")
        print()
    
    # Environment information
    env = report.get('environment', {})
    print("🖥️  ENVIRONMENT:")
    print("-" * 20)
    print(f"Platform: {env.get('platform', 'Unknown')}")
    print(f"Python: {report.get('python_version', 'Unknown').split()[0]}")
    print(f"Project Root: {report.get('project_root', 'Unknown')}")
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("-" * 25)
    
    recommendations = []
    
    # Test-based recommendations
    if stats.get('failed', 0) > 0:
        recommendations.append("🔧 Fix failing tests to improve system reliability")
    
    if stats.get('warnings', 0) > 10:
        recommendations.append("⚠️  Consider addressing test warnings for cleaner output")
    
    # Coverage-based recommendations
    if coverage and coverage['total_coverage'] < 50:
        recommendations.append("📈 Increase test coverage by adding more unit tests")
    
    if coverage and coverage['total_coverage'] > 80:
        recommendations.append("🎉 Excellent coverage! Consider adding integration tests")
    
    # Performance recommendations
    if report['execution_time_seconds'] > 60:
        recommendations.append("⚡ Consider optimizing slow tests or running them separately")
    
    # General recommendations
    if report['test_type'] == 'all' and report['success']:
        recommendations.append("✅ All tests passing! Ready for deployment")
    
    if not recommendations:
        recommendations.append("🎯 System is performing well. Continue regular testing.")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print()
    
    # Quick actions
    print("🚀 QUICK ACTIONS:")
    print("-" * 20)
    print("• Run specific tests: python3 run_tests.py [unit|config|agents|bias]")
    print("• Generate coverage: python3 run_tests.py all --coverage")
    print("• Quick validation: python3 run_tests.py quick")
    print("• View test files: python3 run_tests.py --list-tests")
    print(f"• View detailed log: cat {report['log_file']}")
    
    if coverage:
        coverage_dir = Path(report['project_root']) / "logs" / "coverage"
        if coverage_dir.exists():
            print(f"• View coverage report: open {coverage_dir / 'index.html'}")


def analyze_trends(project_root):
    """Analyze test trends over time (if multiple reports exist)."""
    logs_dir = project_root / "logs"
    
    # Find all test report files
    report_files = list(logs_dir.glob("test_report_*.log"))
    
    if len(report_files) > 1:
        print("\n📊 TEST TRENDS:")
        print("-" * 20)
        print(f"Found {len(report_files)} test reports")
        print("Consider implementing trend analysis for:")
        print("• Success rate over time")
        print("• Coverage improvements")
        print("• Performance trends")
        print("• Most frequently failing tests")


def main():
    """Main function for test summary tool."""
    
    parser = argparse.ArgumentParser(
        description='Yggdrasil Test Summary and Analysis Tool',
        epilog='Analyzes test reports and provides actionable insights'
    )
    
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Project root directory (default: auto-detect)'
    )
    
    args = parser.parse_args()
    
    # Load and analyze the latest report
    report = load_latest_report(args.project_root)
    
    if not report:
        sys.exit(1)
    
    print_test_summary(report)
    analyze_trends(args.project_root)
    
    print("\n" + "=" * 60)
    print("🎯 Run 'python3 run_tests.py' to generate updated reports")
    print("=" * 60)


if __name__ == "__main__":
    main()
