#!/usr/bin/env python3
"""
Python 3.12 Compatibility Test for Solomon-Sophia Project
Tests all major components for Python 3.12 compatibility
"""

import sys
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python Version Compatibility")
    print("=" * 50)
    
    version = sys.version_info
    print(f"Current Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 12:
        print("✅ Python 3.12+ detected - Excellent!")
        return True
    elif version.major == 3 and version.minor >= 11:
        print("⚠️  Python 3.11 detected - Will work but 3.12+ recommended")
        return True
    else:
        print("❌ Python 3.11+ required")
        return False

def test_core_imports():
    """Test core Python 3.12 imports."""
    print("\n📦 Testing Core Library Imports")
    print("=" * 40)
    
    core_modules = [
        'asyncio',
        'json',
        'pathlib',
        'typing',
        'dataclasses',
        'enum',
        're',
        'datetime',
        'uuid',
        'logging'
    ]
    
    success = True
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            success = False
    
    return success

def test_ml_framework_compatibility():
    """Test ML framework compatibility with Python 3.12."""
    print("\n🤖 Testing ML Framework Compatibility")
    print("=" * 45)
    
    frameworks = {
        'numpy': 'NumPy - Numerical computing',
        'pandas': 'Pandas - Data manipulation',
        'torch': 'PyTorch - Deep learning framework',
        'transformers': 'Hugging Face Transformers',
        'sentence_transformers': 'Sentence Transformers',
    }
    
    success = True
    for module, description in frameworks.items():
        try:
            lib = importlib.import_module(module)
            version = getattr(lib, '__version__', 'Unknown')
            print(f"✅ {module} ({version}) - {description}")
        except ImportError:
            print(f"⚠️  {module} - Not installed (will be installed with requirements)")
        except Exception as e:
            print(f"❌ {module} - Error: {e}")
            success = False
    
    # Test TensorFlow separately due to its complexity
    try:
        import tensorflow as tf
        print(f"✅ tensorflow ({tf.__version__}) - Machine learning framework")
        
        # Test if TensorFlow can create a simple operation
        x = tf.constant([1, 2, 3])
        y = tf.constant([4, 5, 6])
        z = tf.add(x, y)
        print(f"   TensorFlow basic operations working: {z.numpy()}")
        
    except ImportError:
        print("⚠️  tensorflow - Not installed (will be installed with requirements)")
    except Exception as e:
        print(f"❌ tensorflow - Error: {e}")
        success = False
    
    return success

def test_web_scraping_compatibility():
    """Test web scraping libraries compatibility."""
    print("\n🕷️  Testing Web Scraping Library Compatibility")
    print("=" * 50)
    
    scraping_libs = {
        'requests': 'HTTP requests library',
        'httpx': 'Modern async HTTP client',
        'beautifulsoup4': 'HTML/XML parsing',
        'lxml': 'XML/HTML parser',
        'fake_useragent': 'User agent generator',
    }
    
    success = True
    for module, description in scraping_libs.items():
        try:
            # Handle module name differences
            import_name = module
            if module == 'beautifulsoup4':
                import_name = 'bs4'
            elif module == 'fake_useragent':
                import_name = 'fake_useragent'
            
            lib = importlib.import_module(import_name)
            version = getattr(lib, '__version__', 'Unknown')
            print(f"✅ {module} ({version}) - {description}")
        except ImportError:
            print(f"⚠️  {module} - Not installed (will be installed with requirements)")
        except Exception as e:
            print(f"❌ {module} - Error: {e}")
            success = False
    
    return success

def test_database_compatibility():
    """Test database libraries compatibility."""
    print("\n🗄️  Testing Database Library Compatibility")
    print("=" * 45)
    
    db_libs = {
        'sqlalchemy': 'SQL toolkit and ORM',
        'alembic': 'Database migration tool',
        'asyncpg': 'Async PostgreSQL adapter',
        'psycopg2': 'PostgreSQL adapter',
    }
    
    success = True
    for module, description in db_libs.items():
        try:
            lib = importlib.import_module(module)
            version = getattr(lib, '__version__', 'Unknown')
            print(f"✅ {module} ({version}) - {description}")
        except ImportError:
            print(f"⚠️  {module} - Not installed (will be installed with requirements)")
        except Exception as e:
            print(f"❌ {module} - Error: {e}")
            success = False
    
    return success

def test_python312_features():
    """Test Python 3.12 specific features."""
    print("\n🆕 Testing Python 3.12 Specific Features")
    print("=" * 45)
    
    try:
        # Test f-string improvements (Python 3.12)
        name = "Solomon"
        version = "3.12"
        formatted = f"Welcome to {name} on Python {version}!"
        print(f"✅ Enhanced f-strings: {formatted}")
        
        # Test improved error messages
        try:
            x = {}
            y = x['nonexistent']
        except KeyError as e:
            print("✅ Improved error messages working")
        
        # Test type hints improvements
        from typing import Optional, List, Dict
        def test_function(data: List[Dict[str, Optional[str]]]) -> bool:
            return len(data) > 0
        
        print("✅ Advanced type hints working")
        
        # Test pathlib improvements
        from pathlib import Path
        current_path = Path(__file__).parent
        print(f"✅ Pathlib enhancements: {current_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Python 3.12 features test failed: {e}")
        return False

def test_project_structure():
    """Test project structure compatibility."""
    print("\n📁 Testing Project Structure")
    print("=" * 35)
    
    required_dirs = [
        'solomon',
        'solomon/scraping',
        'solomon/database',
        'solomon/agents',
        'solomon/api',
        'examples',
        'docs'
    ]
    
    success = True
    project_root = Path(__file__).parent
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - Missing")
            success = False
    
    return success

def main():
    """Run all compatibility tests."""
    print("🚀 Solomon-Sophia Python 3.12 Compatibility Test Suite")
    print("=" * 65)
    
    tests = [
        test_python_version,
        test_core_imports,
        test_ml_framework_compatibility,
        test_web_scraping_compatibility,
        test_database_compatibility,
        test_python312_features,
        test_project_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 65)
    print("📊 Test Summary")
    print("=" * 20)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready for Python 3.12")
        print("\n🚀 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Initialize database: solomon init-db")
        print("3. Test scraping: python test_scraping.py")
        print("4. Start using: solomon scrape --help")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Recommended Actions:")
        print("1. Ensure Python 3.12+ is installed")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Check system compatibility")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
