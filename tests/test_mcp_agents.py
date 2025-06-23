#!/usr/bin/env python3
"""
Test script for MCP-integrated AI agents
Tests all agent functionality through the MCP interface
"""

import asyncio
import json
from yggdrasil_mcp_client import YggdrasilMCPClient

async def test_mcp_agents():
    """Test all MCP agent functionality"""
    
    print("🤖 TESTING MCP-INTEGRATED AI AGENTS")
    print("="*50)
    
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
        theme_text = """
        Love is the fundamental force that connects all beings across different spiritual traditions.
        Whether we speak of divine love in Christianity, compassion in Buddhism, or ahimsa in Hinduism,
        the universal theme of love transcends cultural boundaries and speaks to the human soul.
        """
        
        result = await client.ai_content_analysis(
            text=theme_text,
            analysis_type="theme_analysis",
            tradition="universal",
            domain="spirituality"
        )
        
        client.print_analysis_summary(result)
        
        # Test 3: Doctrine Analysis
        print("\n3. Testing Doctrine Analysis...")
        doctrine_text = """
        The doctrine of the Trinity in Christianity posits that God exists as three persons
        - Father, Son, and Holy Spirit - while remaining one essence. This complex theological
        concept has been central to Christian doctrine since the early church councils.
        """
        
        result = await client.ai_content_analysis(
            text=doctrine_text,
            analysis_type="doctrine_analysis",
            tradition="christianity",
            domain="religion"
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
        
        # Test 6: Comprehensive Analysis
        print("\n6. Testing Comprehensive Analysis...")
        complex_text = """
        The concept of consciousness has been debated by philosophers for centuries.
        Descartes argued for mind-body dualism, while modern materialists claim
        consciousness emerges from neural activity. Buddhist philosophy approaches
        consciousness differently, seeing it as fundamental and unconditioned.
        However, some argue that all these views are based on false premises
        and therefore invalid.
        """
        
        result = await client.ai_content_analysis(
            text=complex_text,
            analysis_type="comprehensive",
            domain="philosophy",
            tradition="mixed"
        )
        
        client.print_analysis_summary(result)
        
        # Test 7: Agent Performance
        print("\n7. Getting Agent Performance Statistics...")
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

if __name__ == "__main__":
    asyncio.run(test_mcp_agents())
