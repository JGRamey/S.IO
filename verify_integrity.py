#!/usr/bin/env python3
"""
Project Integrity Verification Script
Ensures all critical files and functionality remain intact after cleanup
"""

import os
import sys
from pathlib import Path
import importlib.util

def check_file_exists(file_path, description):
    """Check if a critical file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ MISSING {description}: {file_path}")
        return False

def check_directory_exists(dir_path, description):
    """Check if a critical directory exists"""
    if os.path.isdir(dir_path):
        file_count = len(list(Path(dir_path).rglob('*')))
        print(f"✅ {description}: {dir_path} ({file_count} files)")
        return True
    else:
        print(f"❌ MISSING {description}: {dir_path}")
        return False

def test_python_imports():
    """Test that main Python modules can be imported"""
    print("\n🐍 Testing Python Imports:")
    print("-" * 30)
    
    imports_to_test = [
        ('yggdrasil', 'Main application module'),
        ('yggdrasil.config', 'Configuration module'),
        ('yggdrasil.database', 'Database module'),
        ('yggdrasil.agents', 'Agents module'),
        ('yggdrasil.utils', 'Utilities module'),
    ]
    
    all_passed = True
    for module_name, description in imports_to_test:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✅ {description}: {module_name}")
            else:
                print(f"❌ Cannot find {description}: {module_name}")
                all_passed = False
        except Exception as e:
            print(f"❌ Error importing {description}: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run complete integrity verification"""
    print("🔍 S.IO Project Integrity Verification")
    print("=" * 40)
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"📁 Project root: {project_root}")
    print()
    
    # Critical files check
    print("📄 Critical Files Check:")
    print("-" * 25)
    
    critical_files = [
        ("README.md", "Project documentation"),
        ("config/pyproject.toml", "Project configuration"),
        ("pytest.ini", "Test configuration"),
        ("yggdrasil/__init__.py", "Main module init"),
        ("yggdrasil/config.py", "Configuration"),
        ("tests/conftest.py", "Test configuration"),
    ]
    
    files_ok = 0
    for file_path, description in critical_files:
        if check_file_exists(file_path, description):
            files_ok += 1
    
    print()
    
    # Critical directories check
    print("📁 Critical Directories Check:")
    print("-" * 30)
    
    critical_dirs = [
        ("yggdrasil", "Main application code"),
        ("yggdrasil/agents", "AI agents"),
        ("yggdrasil/database", "Database modules"),
        ("yggdrasil/utils", "Utilities"),
        ("tests", "Test files"),
        ("config", "Configuration"),
        ("docs", "Documentation"),
    ]
    
    dirs_ok = 0
    for dir_path, description in critical_dirs:
        if check_directory_exists(dir_path, description):
            dirs_ok += 1
    
    # Test Python imports
    imports_ok = test_python_imports()
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 INTEGRITY VERIFICATION SUMMARY")
    print("=" * 40)
    
    print(f"📄 Critical files: {files_ok}/{len(critical_files)} ✅")
    print(f"📁 Critical directories: {dirs_ok}/{len(critical_dirs)} ✅")
    print(f"🐍 Python imports: {'✅' if imports_ok else '❌'}")
    
    all_checks_passed = (
        files_ok == len(critical_files) and 
        dirs_ok == len(critical_dirs) and 
        imports_ok
    )
    
    if all_checks_passed:
        print("\n🎉 ALL INTEGRITY CHECKS PASSED!")
        print("✅ Project is safe and functional")
        return 0
    else:
        print("\n⚠️  SOME INTEGRITY CHECKS FAILED!")
        print("❌ Review the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
