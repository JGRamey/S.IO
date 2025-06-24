#!/usr/bin/env python3
"""
Yggdrasil MCP Client - Interface for intelligent content processing
Provides easy-to-use interface for the Yggdrasil MCP server
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of content processing"""
    success: bool
    url: str
    analysis: Optional[Dict[str, Any]] = None
    storage_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None

class YggdrasilMCPClient:
    """Client for interacting with Yggdrasil MCP server"""
    
    def __init__(self, server_path: str = None):
        self.server_path = server_path or "/Users/grant/Desktop/Solomon/Database/S.IO/yggdrasil_mcp_server.py"
        self.context_manager = None
        self.session = None
        
    async def connect(self):
        """Connect to the MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python3",
                args=[self.server_path]
            )
            
            self.context_manager = stdio_client(server_params)
            # The stdio_client context manager returns (read, write) streams
            # We need to create the ClientSession from these streams
            read_stream, write_stream = await self.context_manager.__aenter__()
            self.session = ClientSession(read_stream, write_stream)
            await self.session.__aenter__()
            logger.info("Connected to Yggdrasil MCP server")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None
        if self.context_manager:
            await self.context_manager.__aexit__(None, None, None)
            self.context_manager = None
            logger.info("Disconnected from Yggdrasil MCP server")
    
    async def analyze_url(self, url: str) -> ProcessingResult:
        """Analyze a URL to determine optimal storage strategy"""
        
        if not self.session:
            await self.connect()
        
        start_time = datetime.utcnow()
        
        try:
            result = await self.session.call_tool(
                "analyze_data_source",
                {"url": url}
            )
            
            # Parse the result
            result_text = result.content[0].text if result.content else "{}"
            analysis_data = json.loads(result_text.split("Data Source Analysis:\n")[1])
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                url=url,
                analysis=analysis_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error analyzing URL {url}: {e}")
            
            return ProcessingResult(
                success=False,
                url=url,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def intelligent_scrape(self, url: str, force_analysis: bool = False) -> ProcessingResult:
        """Intelligently scrape and store content"""
        
        if not self.session:
            await self.connect()
        
        start_time = datetime.utcnow()
        
        try:
            result = await self.session.call_tool(
                "intelligent_scrape_and_store",
                {"url": url, "force_analysis": force_analysis}
            )
            
            # Parse the result
            result_text = result.content[0].text if result.content else "{}"
            if "Scraping completed successfully:" in result_text:
                storage_data = json.loads(result_text.split("Scraping completed successfully:\n")[1])
            else:
                storage_data = {"raw_response": result_text}
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                url=url,
                storage_info=storage_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error scraping URL {url}: {e}")
            
            return ProcessingResult(
                success=False,
                url=url,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def optimize_storage(self, table_name: str = None) -> Dict[str, Any]:
        """Optimize storage performance"""
        
        if not self.session:
            await self.connect()
        
        try:
            result = await self.session.call_tool(
                "optimize_storage",
                {"table_name": table_name} if table_name else {}
            )
            
            result_text = result.content[0].text if result.content else "{}"
            if "Storage optimization complete:" in result_text:
                return json.loads(result_text.split("Storage optimization complete:\n")[1])
            else:
                return {"raw_response": result_text}
            
        except Exception as e:
            logger.error(f"Error optimizing storage: {e}")
            return {"error": str(e)}
    
    async def get_performance_report(self, domain: str = None) -> Dict[str, Any]:
        """Get query performance report"""
        
        if not self.session:
            await self.connect()
        
        try:
            result = await self.session.call_tool(
                "query_performance_report",
                {"domain": domain} if domain else {}
            )
            
            result_text = result.content[0].text if result.content else "{}"
            if "Performance Report:" in result_text:
                return json.loads(result_text.split("Performance Report:\n")[1])
            else:
                return {"raw_response": result_text}
            
        except Exception as e:
            logger.error(f"Error getting performance report: {e}")
            return {"error": str(e)}
    
    async def batch_process_urls(self, urls: List[str], max_concurrent: int = 5) -> List[ProcessingResult]:
        """Process multiple URLs concurrently"""
        
        logger.info(f"Processing {len(urls)} URLs with max concurrency of {max_concurrent}")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_url(url):
            async with semaphore:
                # First analyze
                analysis_result = await self.analyze_url(url)
                if not analysis_result.success:
                    return analysis_result
                
                # Then scrape if analysis successful
                scrape_result = await self.intelligent_scrape(url)
                
                # Combine results
                return ProcessingResult(
                    success=scrape_result.success,
                    url=url,
                    analysis=analysis_result.analysis,
                    storage_info=scrape_result.storage_info,
                    error_message=scrape_result.error_message,
                    processing_time=(analysis_result.processing_time or 0) + (scrape_result.processing_time or 0)
                )
        
        tasks = [process_single_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ProcessingResult(
                    success=False,
                    url=urls[i],
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def ai_content_analysis(self, text: str, analysis_type: str, **kwargs) -> ProcessingResult:
        """Perform AI-powered content analysis"""
        
        if not self.session:
            await self.connect()
        
        start_time = datetime.utcnow()
        
        try:
            # Prepare arguments
            args = {
                "text": text,
                "analysis_type": analysis_type,
                **kwargs
            }
            
            result = await self.session.call_tool("ai_content_analysis", args)
            
            # Parse the result
            result_text = result.content[0].text if result.content else "{}"
            if "AI Content Analysis Results:" in result_text:
                analysis_data = json.loads(result_text.split("AI Content Analysis Results:\n")[1])
            else:
                analysis_data = {"raw_response": result_text}
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=analysis_data.get("success", False),
                url=kwargs.get("url", "manual_input"),
                analysis=analysis_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error in AI content analysis: {e}")
            
            return ProcessingResult(
                success=False,
                url=kwargs.get("url", "manual_input"),
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def get_analysis_types(self) -> List[Dict[str, str]]:
        """Get available AI analysis types"""
        
        if not self.session:
            await self.connect()
        
        try:
            result = await self.session.call_tool("get_analysis_types", {})
            
            result_text = result.content[0].text if result.content else "[]"
            if "Available AI Analysis Types:" in result_text:
                return json.loads(result_text.split("Available AI Analysis Types:\n")[1])
            else:
                return []
            
        except Exception as e:
            logger.error(f"Error getting analysis types: {e}")
            return []
    
    async def get_agent_performance(self) -> Dict[str, Any]:
        """Get AI agent performance statistics"""
        
        if not self.session:
            await self.connect()
        
        try:
            result = await self.session.call_tool("agent_performance_report", {})
            
            result_text = result.content[0].text if result.content else "{}"
            if "Agent Performance Report:" in result_text:
                return json.loads(result_text.split("Agent Performance Report:\n")[1])
            else:
                return {"raw_response": result_text}
            
        except Exception as e:
            logger.error(f"Error getting agent performance: {e}")
            return {"error": str(e)}

    def print_analysis_summary(self, result: ProcessingResult):
        """Print a formatted analysis summary"""
        
        print(f"\n{'='*60}")
        print(f"ANALYSIS SUMMARY: {result.url}")
        print(f"{'='*60}")
        
        if not result.success:
            print(f"❌ FAILED: {result.error_message}")
            return
        
        if result.analysis:
            analysis = result.analysis
            print(f"✅ SUCCESS")
            
            # Handle different types of analysis results
            if "analysis_type" in analysis:
                print(f"Analysis Type: {analysis.get('analysis_type', 'Unknown')}")
                
                # Display results based on analysis type
                results = analysis.get("results", {})
                
                if "detected_themes" in results:
                    print(f"\n🎯 Detected Themes:")
                    for theme in results["detected_themes"][:3]:  # Show top 3
                        print(f"  - {theme.get('theme_name', 'Unknown')}: {theme.get('confidence_score', 0):.2f}")
                
                if "detected_doctrines" in results:
                    print(f"\n📜 Detected Doctrines:")
                    for doctrine in results["detected_doctrines"][:3]:
                        print(f"  - {doctrine.get('doctrine_name', 'Unknown')}: {doctrine.get('confidence_score', 0):.2f}")
                
                if "detected_fallacies" in results:
                    print(f"\n⚠️  Detected Fallacies:")
                    for fallacy in results["detected_fallacies"][:3]:
                        print(f"  - {fallacy.get('fallacy_type', 'Unknown')}: {fallacy.get('confidence_score', 0):.2f}")
                
                if "storage_strategy" in results:
                    print(f"\n💾 Storage Strategy: {results['storage_strategy']}")
                    print(f"Confidence: {results.get('confidence_score', 0):.2f}")
                
                if "complexity_metrics" in results:
                    metrics = results["complexity_metrics"]
                    print(f"\n📊 Complexity Metrics:")
                    print(f"  Semantic Complexity: {metrics.get('semantic_complexity', 0):.2f}")
                    print(f"  Topic Coherence: {metrics.get('topic_coherence', 0):.2f}")
                    print(f"  Information Density: {metrics.get('information_density', 0):.2f}")
                    print(f"  Query Potential: {metrics.get('query_potential', 0):.2f}")
            
            else:
                # Legacy analysis format
                print(f"Content Type: {analysis.get('content_type', 'Unknown')}")
                print(f"Domain: {analysis.get('domain', 'Unknown')}")
                print(f"Estimated Size: {self._format_size(analysis.get('estimated_size', 0))}")
                print(f"Language: {analysis.get('language', 'Unknown')}")
                print(f"Storage Strategy: {analysis.get('storage_strategy', 'Unknown')}")
                print(f"Confidence Score: {analysis.get('confidence_score', 0):.2f}")
                
                if analysis.get('table_name'):
                    print(f"Dynamic Table: {analysis['table_name']}")
                
                # Complexity metrics
                print(f"\nComplexity Metrics:")
                print(f"  Semantic Complexity: {analysis.get('complexity_score', 0):.2f}")
        
        if result.storage_info:
            print(f"\nStorage Information:")
            print(f"  Status: {result.storage_info.get('status', 'Unknown')}")
            
        if result.processing_time:
            print(f"\nProcessing Time: {result.processing_time:.2f} seconds")
        
        print(f"{'='*60}\n")

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

# Convenience functions for common use cases
async def quick_analyze(url: str) -> ProcessingResult:
    """Quick analysis of a single URL"""
    client = YggdrasilMCPClient()
    try:
        result = await client.analyze_url(url)
        return result
    finally:
        await client.disconnect()

async def smart_scrape(url: str) -> ProcessingResult:
    """Smart scraping of a single URL"""
    client = YggdrasilMCPClient()
    try:
        result = await client.intelligent_scrape(url)
        return result
    finally:
        await client.disconnect()

async def batch_smart_scrape(urls: List[str], max_concurrent: int = 3) -> List[ProcessingResult]:
    """Batch smart scraping of multiple URLs"""
    client = YggdrasilMCPClient()
    try:
        results = await client.batch_process_urls(urls, max_concurrent)
        return results
    finally:
        await client.disconnect()

# CLI Interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Yggdrasil Intelligent Content Processor")
    parser.add_argument("command", choices=["analyze", "scrape", "batch", "optimize", "report", "ai_analyze"], 
                       help="Command to execute")
    parser.add_argument("--url", help="URL to process (for analyze/scrape)")
    parser.add_argument("--urls-file", help="File containing URLs to process (for batch)")
    parser.add_argument("--domain", help="Domain for reports")
    parser.add_argument("--table", help="Table name for optimization")
    parser.add_argument("--concurrent", type=int, default=3, help="Max concurrent processing")
    parser.add_argument("--text", help="Text to analyze (for ai_analyze)")
    parser.add_argument("--analysis-type", help="Analysis type (for ai_analyze)")
    
    args = parser.parse_args()
    
    client = YggdrasilMCPClient()
    
    try:
        await client.connect()
        
        if args.command == "analyze":
            if not args.url:
                print("❌ URL required for analyze command")
                return
            
            print(f"🔍 Analyzing: {args.url}")
            result = await client.analyze_url(args.url)
            client.print_analysis_summary(result)
        
        elif args.command == "scrape":
            if not args.url:
                print("❌ URL required for scrape command")
                return
            
            print(f"🌐 Scraping: {args.url}")
            result = await client.intelligent_scrape(args.url)
            client.print_analysis_summary(result)
        
        elif args.command == "batch":
            if not args.urls_file:
                print("❌ URLs file required for batch command")
                return
            
            try:
                with open(args.urls_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"❌ URLs file not found: {args.urls_file}")
                return
            
            print(f"📦 Batch processing {len(urls)} URLs...")
            results = await client.batch_process_urls(urls, args.concurrent)
            
            # Summary
            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful
            
            print(f"\n📊 BATCH PROCESSING SUMMARY")
            print(f"Total URLs: {len(urls)}")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            
            if failed > 0:
                print(f"\n❌ FAILED URLs:")
                for result in results:
                    if not result.success:
                        print(f"  - {result.url}: {result.error_message}")
        
        elif args.command == "optimize":
            print("🔧 Optimizing storage...")
            result = await client.optimize_storage(args.table)
            print(json.dumps(result, indent=2))
        
        elif args.command == "report":
            print("📈 Generating performance report...")
            result = await client.get_performance_report(args.domain)
            print(json.dumps(result, indent=2))
        
        elif args.command == "ai_analyze":
            if not args.text:
                print("❌ Text required for ai_analyze command")
                return
            
            if not args.analysis_type:
                print("❌ Analysis type required for ai_analyze command")
                return
            
            print(f"🤖 Analyzing text with {args.analysis_type}...")
            result = await client.ai_content_analysis(args.text, args.analysis_type)
            client.print_analysis_summary(result)
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
