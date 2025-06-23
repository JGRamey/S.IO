#!/usr/bin/env python3
"""Test script to run inside Docker container"""

import asyncio
import sys
sys.path.append('/app/yggdrasil')

from yggdrasil.scraping.yggdrasil_manager import YggdrasilScrapingManager

async def test_yggdrasil():
    print("🌳 Testing Yggdrasil Inside Docker...")
    
    try:
        manager = YggdrasilScrapingManager()
        await manager.initialize()
        print("✅ Yggdrasil manager initialized")
        
        # Test academic scraping
        config = {
            "wikipedia_categories": ["Philosophy"],
            "category_limit": 2
        }
        
        results = await manager.scrape_academic_content(config)
        print(f"✅ Scraped {results.get('scraped_articles', 0)} articles")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_yggdrasil())
