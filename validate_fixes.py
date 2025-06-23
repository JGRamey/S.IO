#!/usr/bin/env python3
"""Validate the import and configuration fixes."""

import os
import sys
from pathlib import Path

def validate_files_exist():
    """Check that all critical files exist."""
    print("🔍 Checking file structure...")
    
    critical_files = [
        "yggdrasil/config.py",
        "yggdrasil/database/__init__.py", 
        "yggdrasil/database/models.py",
        "yggdrasil/database/connection.py",
        "yggdrasil/utils/__init__.py",
        "yggdrasil/utils/logging.py",
        "yggdrasil/utils/exceptions.py",
        "tests/conftest.py",
        "tests/test_config.py",
        "deployment/docker/.env",
        ".env.template",
        "pytest.ini",
        "run_tests.py"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("\n✅ All critical files present")
    return True

def validate_import_statements():
    """Check import statements in key files."""
    print("\n🔍 Validating import statements...")
    
    # Check database __init__.py for correct imports
    db_init_path = Path("yggdrasil/database/__init__.py")
    if db_init_path.exists():
        content = db_init_path.read_text()
        if "YggdrasilText" in content and "SpiritualText" not in content:
            print("  ✅ Database __init__.py has correct YggdrasilText import")
        else:
            print("  ❌ Database __init__.py still has SpiritualText import")
            return False
    
    # Check for remaining solomon references
    solomon_files = []
    for py_file in Path("yggdrasil").rglob("*.py"):
        try:
            content = py_file.read_text()
            if "solomon.config" in content or "solomon." in content:
                solomon_files.append(str(py_file))
        except:
            pass
    
    if solomon_files:
        print(f"  ❌ Files still referencing 'solomon': {solomon_files}")
        return False
    else:
        print("  ✅ No remaining 'solomon' references found")
    
    return True

def validate_requirements():
    """Check that requirements.txt has necessary dependencies."""
    print("\n🔍 Validating requirements.txt...")
    
    req_path = Path("config/requirements.txt")
    if not req_path.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    content = req_path.read_text()
    required_deps = ["qdrant-client", "tenacity", "pydantic", "sqlalchemy"]
    
    missing_deps = []
    for dep in required_deps:
        if dep not in content:
            missing_deps.append(dep)
        else:
            print(f"  ✅ {dep} found in requirements")
    
    if missing_deps:
        print(f"  ❌ Missing dependencies: {missing_deps}")
        return False
    
    return True

def validate_docker_config():
    """Check Docker configuration."""
    print("\n🔍 Validating Docker configuration...")
    
    # Check .env file
    env_path = Path("deployment/docker/.env")
    if env_path.exists():
        content = env_path.read_text()
        if "POSTGRES_PASSWORD=" in content and "DATABASE_URL=" in content:
            print("  ✅ Docker .env file has required variables")
        else:
            print("  ❌ Docker .env file missing critical variables")
            return False
    else:
        print("  ❌ Docker .env file not found")
        return False
    
    # Check docker-compose.yml
    compose_path = Path("deployment/docker/docker-compose.yml")
    if compose_path.exists():
        content = compose_path.read_text()
        if "${DATABASE_URL}" in content and "5431:5431" in content:
            print("  ✅ Docker compose has environment variables and correct ports")
        else:
            print("  ❌ Docker compose missing environment variables or wrong ports")
            return False
    
    return True

def main():
    """Run all validations."""
    print("🎯 S.IO IMPROVEMENT VALIDATION")
    print("=" * 50)
    
    validations = [
        ("File Structure", validate_files_exist),
        ("Import Statements", validate_import_statements), 
        ("Requirements", validate_requirements),
        ("Docker Config", validate_docker_config)
    ]
    
    all_passed = True
    results = []
    
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append((name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"  ❌ {name} validation failed with error: {e}")
            results.append((name, False))
            all_passed = False
    
    print("\n📊 VALIDATION SUMMARY")
    print("-" * 10)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}")
    
    if all_passed:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("The S.IO system is properly configured and ready for deployment.")
        return True
    else:
        print("\n⚠️  Some validations failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
