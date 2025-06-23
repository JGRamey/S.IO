#!/usr/bin/env python3
"""
Test script for MCP-integrated AI agents
Tests all agent functionality through the MCP interface
"""

import asyncio
import json
import sys
import os
import pytest

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from yggdrasil_mcp.client.yggdrasil_mcp_client import YggdrasilMCPClient
from test_config import get_test_settings, SAMPLE_SPIRITUAL_TEXT, SAMPLE_PHILOSOPHICAL_TEXT, BIASED_TEXT_SAMPLE

@pytest.mark.asyncio
async def test_mcp_agents():
    """Test all MCP agent functionality"""
    
    print("🤖 TESTING MCP-INTEGRATED AI AGENTS")
    print("="*50)
    
    # Use test configuration
    test_settings = get_test_settings()
    print(f"Using test database: {test_settings.postgres_db}")
    
    client = YggdrasilMCPClient()
    
    try:
        await client.connect()
        
        # Test 1: Get available analysis types
        print("\n1. Getting available analysis types...")
        analysis_types = await client.get_analysis_types()
        
        print("Available AI Analysis Types:")
        for analysis_type in analysis_types:
            print(f"  - {analysis_type['name']}: {analysis_type['description']}")
        
        # Test 2: Theme Analysis
        print("\n2. Testing Theme Analysis...")
        
        result = await client.ai_content_analysis(
            text=SAMPLE_SPIRITUAL_TEXT,
            analysis_type="theme_analysis",
            tradition="universal",
            domain="spirituality"
        )
        
        client.print_analysis_summary(result)
        
        # Test 3: Doctrine Analysis
        print("\n3. Testing Doctrine Analysis...")
        
        result = await client.ai_content_analysis(
            text=SAMPLE_SPIRITUAL_TEXT,
            analysis_type="doctrine_analysis",
            tradition="christianity",
            domain="theology"
        )
        
        client.print_analysis_summary(result)
        
        # Test 4: Fallacy Detection
        print("\n4. Testing Fallacy Detection...")
        fallacy_text = """
        Everyone knows that meditation is useless because my neighbor tried it once and didn't
        become enlightened immediately. Either you achieve instant enlightenment or meditation
        is completely worthless. Since most people don't become enlightened, clearly meditation
        is a waste of time for everyone.
        """
        
        result = await client.ai_content_analysis(
            text=fallacy_text,
            analysis_type="fallacy_detection",
            domain="philosophy"
        )
        
        client.print_analysis_summary(result)
        
        # Test 5: Storage Optimization
        print("\n5. Testing Storage Optimization...")
        large_text = """
        This is a sample of a much larger philosophical treatise that would typically
        contain tens of thousands of words discussing complex metaphysical concepts,
        detailed arguments, extensive quotations from historical sources, and comprehensive
        analysis of various philosophical positions. In a real scenario, this would be
        a complete book or academic paper requiring intelligent storage decisions.
        """ * 100  # Make it larger
        
        result = await client.ai_content_analysis(
            text=large_text,
            analysis_type="storage_optimization",
            domain="philosophy",
            url="https://example.com/large-treatise"
        )
        
        client.print_analysis_summary(result)
        
        # Test 6: Bias Detection
        print("\n6. Testing Bias Detection...")
        
        result = await client.ai_content_analysis(
            text=BIASED_TEXT_SAMPLE,
            analysis_type="bias_detection",
            domain="philosophy",
            tradition="western"
        )
        
        client.print_analysis_summary(result)
        
        # Test 7: Comprehensive Analysis
        print("\n7. Testing Comprehensive Analysis...")
        
        result = await client.ai_content_analysis(
            text=SAMPLE_PHILOSOPHICAL_TEXT,
            analysis_type="comprehensive",
            domain="philosophy",
            tradition="mixed"
        )
        
        client.print_analysis_summary(result)
        
        # Test 8: Agent Performance
        print("\n8. Getting Agent Performance Statistics...")
        performance = await client.get_agent_performance()
        
        print("Agent Performance Report:")
        print(json.dumps(performance, indent=2))
        
        print("\n✅ All MCP agent tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in MCP agent testing: {e}")
        
    finally:
        await client.disconnect()

# Convenience functions for specific analyses
async def quick_theme_analysis(text: str, tradition: str = "universal"):
    """Quick theme analysis"""
    client = YggdrasilMCPClient()
    try:
        result = await client.ai_content_analysis(text, "theme_analysis", tradition=tradition)
        return result
    finally:
        await client.disconnect()

async def quick_fallacy_check(text: str):
    """Quick fallacy detection"""
    client = YggdrasilMCPClient()
    try:
        result = await client.ai_content_analysis(text, "fallacy_detection")
        return result
    finally:
        await client.disconnect()

async def quick_storage_optimization(text: str, url: str = None):
    """Quick storage optimization analysis"""
    client = YggdrasilMCPClient()
    try:
        result = await client.ai_content_analysis(text, "storage_optimization", url=url)
        return result
    finally:
        await client.disconnect()

async def quick_bias_detection(text: str, domain: str = "philosophy"):
    """Quick bias detection analysis"""
    client = YggdrasilMCPClient()
    try:
        result = await client.ai_content_analysis(text, "bias_detection", domain=domain)
        return result
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_mcp_agents())
