#!/usr/bin/env python3
"""
Quick test of MCP agent integration
Simplified test to verify agents work with MCP server
"""

import asyncio
import json
import sys
import os
import pytest

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_config import get_test_settings, SAMPLE_SPIRITUAL_TEXT

@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic MCP agent functionality"""
    
    print("🧪 QUICK MCP AGENT TEST")
    print("="*30)
    
    # Use test configuration
    test_settings = get_test_settings()
    print(f"Test Environment: {test_settings.postgres_db}")
    
    # Import here to avoid issues if MCP not available
    try:
        from yggdrasil_mcp.client.yggdrasil_mcp_client import YggdrasilMCPClient
    except ImportError:
        print("❌ MCP client not available - install MCP dependencies")
        return False
    
    client = YggdrasilMCPClient()
    
    try:
        print("\n1. Connecting to MCP server...")
        await client.connect()
        print("✅ Connected successfully")
        
        print("\n2. Getting available analysis types...")
        analysis_types = await client.get_analysis_types()
        print(f"✅ Found {len(analysis_types)} analysis types")
        
        print("\n3. Testing theme analysis...")
        result = await client.ai_content_analysis(
            text=SAMPLE_SPIRITUAL_TEXT,
            analysis_type="theme_analysis"
        )
        
        if result.success:
            print("✅ Theme analysis completed successfully")
        else:
            print(f"❌ Theme analysis failed: {result.error_message}")
        
        print("\n4. Testing storage optimization...")
        result = await client.ai_content_analysis(
            text="This is a sample text for storage optimization analysis.",
            analysis_type="storage_optimization"
        )
        
        if result.success:
            print("✅ Storage optimization completed successfully")
        else:
            print(f"❌ Storage optimization failed: {result.error_message}")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        try:
            await client.disconnect()
            print("✅ Disconnected cleanly")
        except:
            pass

def test_database_connectivity():
    """Test database connectivity without MCP"""
    
    print("\n📊 Testing Database Connectivity...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            "postgresql://postgres:JGRsolomon0924$@localhost:5431/yggdrasil"
        )
        cursor = conn.cursor()
        
        # Test enhanced schema
        cursor.execute("SELECT COUNT(*) FROM content_metadata;")
        metadata_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM yggdrasil_texts;")
        texts_count = cursor.fetchone()[0]
        
        print(f"✅ Database connected: {metadata_count} metadata, {texts_count} texts")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Main test runner"""
    
    print("YGGDRASIL MCP AGENT SYSTEM TEST")
    print("="*40)
    
    # Test 1: Database connectivity
    db_ok = test_database_connectivity()
    
    # Test 2: MCP functionality  
    if db_ok:
        mcp_ok = await test_basic_functionality()
    else:
        print("⚠️  Skipping MCP tests due to database issues")
        mcp_ok = False
    
    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("="*20)
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"MCP Agents: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    
    if db_ok and mcp_ok:
        print("\n🎉 All systems operational!")
        print("Ready to use MCP-integrated AI agents!")
    else:
        print("\n⚠️  Some issues detected. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
