#!/usr/bin/env python3
"""Quick deployment test script for S.IO/Yggdrasil system."""

import requests
import time
import json
from typing import Dict, Any

def test_api_endpoint(url: str, endpoint: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test an API endpoint and return results."""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=10)
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "success": response.status_code == expected_status,
            "response_size": len(response.text),
            "error": None
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": None,
            "success": False,
            "response_size": 0,
            "error": str(e)
        }

def main():
    """Run deployment tests."""
    print("🚀 S.IO Deployment Test Suite")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Wait for service to be ready
    print("⏳ Waiting for service to be ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Service is ready!")
                break
        except:
            pass
        
        if i == max_retries - 1:
            print("❌ Service failed to start within timeout")
            return
            
        time.sleep(2)
        print(f"   Attempt {i+1}/{max_retries}...")
    
    # Test endpoints
    endpoints_to_test = [
        "/health",
        "/health/database", 
        "/health/agents",
        "/docs",
        "/openapi.json"
    ]
    
    print("\n🧪 Testing API Endpoints:")
    print("-" * 10)
    
    results = []
    for endpoint in endpoints_to_test:
        result = test_api_endpoint(base_url, endpoint)
        results.append(result)
        
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {endpoint}: {result['status_code']} ({result.get('error', 'OK')})")
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n📊 Test Summary:")
    print(f"   Passed: {successful}/{total}")
    print(f"   Success Rate: {successful/total*100:.1f}%")
    
    if successful == total:
        print("\n🎉 All deployment tests passed! System is ready.")
    else:
        print(f"\n⚠️  {total-successful} tests failed. Check logs for details.")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
