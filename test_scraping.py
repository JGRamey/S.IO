#!/usr/bin/env python3
"""
Test script for Solomon webscraping functionality.
Run this to test the scraping system before using it in production.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from solomon.database import DatabaseManager
from solomon.database.models import TextType
from solomon.scraping.scraping_manager import ScrapingManager


async def test_scraping():
    """Test the scraping functionality."""
    print("🔍 Testing Solomon Webscraping System")
    print("=" * 50)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        db_manager = DatabaseManager()
        await db_manager.initialize()
        print("✅ Database initialized successfully")
        
        # Initialize scraping manager
        print("🕷️  Initializing scraping manager...")
        scraping_manager = ScrapingManager(db_manager)
        print("✅ Scraping manager initialized")
        
        # Test configuration creation
        print("⚙️  Creating test configuration...")
        config = scraping_manager.create_scraping_config(
            [TextType.BIBLE],
            bible_books=['genesis'],
            bible_versions=['NIV'],
            min_quality=0.3,
            max_texts_per_type=5  # Small number for testing
        )
        print("✅ Configuration created")
        print(f"   Config: {config}")
        
        # Test scraping status
        print("📈 Checking current database status...")
        status = await scraping_manager.get_scraping_status()
        print("✅ Status retrieved")
        print(f"   Total texts: {status['total_texts']}")
        print(f"   Supported types: {', '.join(status['supported_types'])}")
        
        # Test small scraping operation
        print("🔄 Testing small scraping operation...")
        print("   (This will scrape a few verses from Genesis)")
        
        # Create a minimal test request
        test_requests = [
            {
                "text_type": "bible",
                "passage": {
                    "book": "genesis",
                    "chapter": 1,
                    "verse_start": 1,
                    "verse_end": 3,
                    "version": "NIV"
                }
            }
        ]
        
        results = await scraping_manager.scrape_specific_texts(test_requests)
        print("✅ Test scraping completed")
        print(f"   Requests processed: {results['requests_processed']}")
        print(f"   Texts scraped: {results['texts_scraped']}")
        print(f"   Texts saved: {results['texts_saved']}")
        
        if results.get('errors'):
            print(f"⚠️  Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:3]:  # Show first 3 errors
                print(f"     • {error}")
        
        # Final status check
        print("📊 Final database status...")
        final_status = await scraping_manager.get_scraping_status()
        print(f"   Total texts after test: {final_status['total_texts']}")
        
        print("\n🎉 Test completed successfully!")
        print("   The scraping system is ready to use.")
        print("   Run 'solomon scrape --help' for usage instructions.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        print("Full error details:")
        print(traceback.format_exc())
        return False
    
    return True


async def test_text_processing():
    """Test the text processing functionality."""
    print("\n🔧 Testing Text Processing")
    print("=" * 30)
    
    try:
        from solomon.scraping.text_processor import TextProcessor
        from solomon.scraping.base_scraper import ScrapedText
        
        processor = TextProcessor()
        
        # Create a sample scraped text
        sample_text = ScrapedText(
            title="Genesis 1:1",
            content="In the beginning God created the heavens and the earth.",
            text_type=TextType.BIBLE,
            language="english",
            book="Genesis",
            chapter=1,
            verse=1,
            source_url="https://example.com"
        )
        
        # Process the text
        processed = processor.process_single_text(sample_text)
        
        print("✅ Text processing successful")
        print(f"   Word count: {processed.word_count}")
        print(f"   Quality score: {processed.quality_score:.2f}")
        print(f"   Themes: {', '.join(processed.themes) if processed.themes else 'None detected'}")
        print(f"   Keywords: {', '.join(processed.keywords[:5]) if processed.keywords else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text processing test failed: {str(e)}")
        return False


def main():
    """Main test function."""
    print("🚀 Solomon Webscraping Test Suite")
    print("=" * 60)
    
    # Check if we can import required modules
    try:
        from solomon.scraping import ScrapingManager
        print("✅ All scraping modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("   Make sure you've installed all dependencies:")
        print("   pip install -r requirements.txt")
        return
    
    # Run async tests
    success = asyncio.run(test_scraping())
    
    if success:
        # Run text processing test
        asyncio.run(test_text_processing())
        
        print("\n" + "=" * 60)
        print("🎯 Next Steps:")
        print("1. Run 'solomon scrape-status' to check database")
        print("2. Run 'solomon scrape --types bible --verbose' for full scraping")
        print("3. See docs/WEBSCRAPING_GUIDE.md for detailed usage")
        print("4. Use 'solomon analyze' to analyze scraped texts")
    else:
        print("\n❌ Tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
