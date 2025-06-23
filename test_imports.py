#!/usr/bin/env python3
"""Simple import test to verify our module structure."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test basic imports to verify project structure."""
    print("🧪 Testing Basic Imports")
    print("=" * 30)
    
    tests = []
    
    # Test 1: Basic config import
    try:
        from yggdrasil.config import settings
        tests.append(("✅", "yggdrasil.config", "OK"))
        print(f"Database URL: {settings.database_url}")
        print(f"Qdrant URL: {settings.qdrant_url}")
    except Exception as e:
        tests.append(("❌", "yggdrasil.config", str(e)))
    
    # Test 2: Database models import  
    try:
        from yggdrasil.database.models import YggdrasilText, Base
        tests.append(("✅", "yggdrasil.database.models", "OK"))
    except Exception as e:
        tests.append(("❌", "yggdrasil.database.models", str(e)))
    
    # Test 3: Utils import
    try:
        from yggdrasil.utils.exceptions import YggdrasilException
        from yggdrasil.utils.logging import get_logger
        tests.append(("✅", "yggdrasil.utils", "OK"))
    except Exception as e:
        tests.append(("❌", "yggdrasil.utils", str(e)))
    
    # Test 4: Database connection import
    try:
        from yggdrasil.database.connection import DatabaseManager
        tests.append(("✅", "yggdrasil.database.connection", "OK"))
    except Exception as e:
        tests.append(("❌", "yggdrasil.database.connection", str(e)))
    
    # Print results
    print("\n📊 Import Test Results:")
    print("-" * 50)
    for status, module, result in tests:
        print(f"{status} {module:<30} {result}")
    
    # Summary
    passed = sum(1 for test in tests if test[0] == "✅")
    total = len(tests)
    print(f"\n🎯 Summary: {passed}/{total} imports successful")
    
    if passed == total:
        print("🎉 All imports working! Module structure is correct.")
        return True
    else:
        print("⚠️  Some imports failed. Check dependencies.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
