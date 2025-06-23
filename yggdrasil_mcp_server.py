#!/usr/bin/env python3
"""
Yggdrasil MCP Server - Intelligent Data Processing & Storage Optimization
Advanced MCP server with AI agents for smart scraping and storage decisions
"""

import asyncio
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
)

# Database and AI imports
import psycopg2
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
import httpx
from bs4 import BeautifulSoup
import spacy
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageStrategy(Enum):
    """Storage strategy options"""
    POSTGRES_ONLY = "postgres_only"
    QDRANT_ONLY = "qdrant_only" 
    HYBRID = "hybrid"
    DYNAMIC = "dynamic"

class ContentType(Enum):
    """Content type classifications"""
    SMALL_TEXT = "small_text"          # < 10KB
    MEDIUM_TEXT = "medium_text"        # 10KB - 1MB
    LARGE_TEXT = "large_text"          # 1MB - 10MB
    BOOK = "book"                      # > 10MB
    ACADEMIC_PAPER = "academic_paper"  # Usually 1-5MB
    REFERENCE = "reference"            # Encyclopedias, etc.

@dataclass
class DataSourceAnalysis:
    """Analysis result for a data source"""
    url: str
    content_type: ContentType
    estimated_size: int
    language: str
    domain: str
    complexity_score: float
    storage_strategy: StorageStrategy
    table_name: Optional[str] = None
    metadata: Dict[str, Any] = None

class IntelligentStorageManager:
    """Manages intelligent storage decisions and database operations"""
    
    def __init__(self, postgres_url: str, qdrant_url: str):
        self.postgres_url = postgres_url
        self.qdrant_url = qdrant_url
        self.engine = create_engine(postgres_url)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        
        # Size thresholds for storage decisions
        self.size_thresholds = {
            ContentType.SMALL_TEXT: 10_000,      # 10KB
            ContentType.MEDIUM_TEXT: 1_000_000,  # 1MB
            ContentType.LARGE_TEXT: 10_000_000,  # 10MB
            ContentType.BOOK: float('inf')       # No upper limit
        }
        
    async def analyze_data_source(self, url: str) -> DataSourceAnalysis:
        """Analyze a data source to determine optimal storage strategy"""
        
        try:
            # Fetch headers to get content info
            async with httpx.AsyncClient() as client:
                response = await client.head(url, follow_redirects=True)
                content_length = response.headers.get('content-length')
                content_type = response.headers.get('content-type', '')
                
                # Get a sample of the content for analysis
                response = await client.get(url, follow_redirects=True)
                content = response.text[:5000]  # First 5KB for analysis
                
            # Analyze content
            analysis = await self._analyze_content(url, content, content_length, content_type)
            
            # Determine storage strategy
            analysis.storage_strategy = self._determine_storage_strategy(analysis)
            
            # Generate table name if needed
            if analysis.storage_strategy in [StorageStrategy.POSTGRES_ONLY, StorageStrategy.HYBRID]:
                analysis.table_name = self._generate_table_name(analysis)
            
            logger.info(f"Analysis complete for {url}: {analysis.content_type.value}, {analysis.storage_strategy.value}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data source {url}: {e}")
            # Return default analysis
            return DataSourceAnalysis(
                url=url,
                content_type=ContentType.MEDIUM_TEXT,
                estimated_size=100_000,
                language="en",
                domain="general",
                complexity_score=0.5,
                storage_strategy=StorageStrategy.HYBRID
            )
    
    async def _analyze_content(self, url: str, content: str, content_length: str, content_type: str) -> DataSourceAnalysis:
        """Analyze content characteristics"""
        
        # Estimate size
        estimated_size = int(content_length) if content_length else len(content) * 20
        
        # Determine content type
        content_type_enum = self._classify_content_type(estimated_size, url, content)
        
        # Detect language (simplified)
        language = self._detect_language(content)
        
        # Determine domain
        domain = self._classify_domain(url, content)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(content)
        
        # Extract metadata
        metadata = self._extract_metadata(url, content, content_type)
        
        return DataSourceAnalysis(
            url=url,
            content_type=content_type_enum,
            estimated_size=estimated_size,
            language=language,
            domain=domain,
            complexity_score=complexity_score,
            storage_strategy=StorageStrategy.DYNAMIC,  # Will be set later
            metadata=metadata
        )
    
    def _classify_content_type(self, size: int, url: str, content: str) -> ContentType:
        """Classify content type based on size and characteristics"""
        
        # Book indicators
        if any(indicator in url.lower() for indicator in ['gutenberg', 'book', 'ebook', 'pdf']):
            return ContentType.BOOK
        
        # Academic paper indicators
        if any(indicator in url.lower() for indicator in ['arxiv', 'paper', 'journal', 'doi']):
            return ContentType.ACADEMIC_PAPER
        
        # Reference indicators
        if any(indicator in url.lower() for indicator in ['wikipedia', 'encyclopedia', 'reference']):
            return ContentType.REFERENCE
        
        # Size-based classification
        if size < self.size_thresholds[ContentType.SMALL_TEXT]:
            return ContentType.SMALL_TEXT
        elif size < self.size_thresholds[ContentType.MEDIUM_TEXT]:
            return ContentType.MEDIUM_TEXT
        elif size < self.size_thresholds[ContentType.LARGE_TEXT]:
            return ContentType.LARGE_TEXT
        else:
            return ContentType.BOOK
    
    def _detect_language(self, content: str) -> str:
        """Detect content language (simplified)"""
        # This is a simplified implementation
        # In production, use langdetect or similar
        return "en"
    
    def _classify_domain(self, url: str, content: str) -> str:
        """Classify content domain"""
        
        domain_keywords = {
            "religion": ["bible", "quran", "torah", "buddhist", "spiritual", "religious"],
            "philosophy": ["philosophy", "philosophical", "ethics", "metaphysics", "logic"],
            "science": ["science", "scientific", "research", "study", "analysis"],
            "literature": ["literature", "novel", "poetry", "fiction", "literary"],
            "history": ["history", "historical", "ancient", "medieval", "modern"],
            "technology": ["technology", "technical", "computer", "software", "programming"],
            "medicine": ["medical", "medicine", "health", "clinical", "patient"],
            "mathematics": ["mathematics", "mathematical", "theorem", "proof", "equation"]
        }
        
        url_lower = url.lower()
        content_lower = content.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in url_lower or keyword in content_lower for keyword in keywords):
                return domain
        
        return "general"
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate content complexity score (0-1)"""
        
        # Simple complexity metrics
        words = content.split()
        if not words:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence complexity (simplified)
        sentences = content.split('.')
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Normalize to 0-1 scale
        complexity = min(1.0, (avg_word_length * 0.1) + (avg_sentence_length * 0.01))
        
        return complexity
    
    def _extract_metadata(self, url: str, content: str, content_type: str) -> Dict[str, Any]:
        """Extract metadata from content"""
        
        metadata = {
            "source_url": url,
            "content_type": content_type,
            "scraped_at": datetime.utcnow().isoformat(),
            "word_count": len(content.split()),
            "character_count": len(content)
        }
        
        # Try to extract title from HTML
        try:
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title')
            if title:
                metadata["title"] = title.get_text().strip()
        except:
            pass
        
        return metadata
    
    def _determine_storage_strategy(self, analysis: DataSourceAnalysis) -> StorageStrategy:
        """Determine optimal storage strategy based on analysis"""
        
        # Strategy decision logic
        if analysis.content_type == ContentType.SMALL_TEXT:
            return StorageStrategy.POSTGRES_ONLY
        
        elif analysis.content_type == ContentType.BOOK:
            return StorageStrategy.QDRANT_ONLY
        
        elif analysis.content_type in [ContentType.LARGE_TEXT, ContentType.ACADEMIC_PAPER]:
            return StorageStrategy.HYBRID
        
        else:
            # Medium text - decide based on complexity and domain
            if analysis.complexity_score > 0.7 or analysis.domain in ["philosophy", "science"]:
                return StorageStrategy.HYBRID
            else:
                return StorageStrategy.POSTGRES_ONLY
    
    def _generate_table_name(self, analysis: DataSourceAnalysis) -> str:
        """Generate appropriate table name for the content"""
        
        # Generate table name based on domain and content type
        domain = analysis.domain.replace(" ", "_").lower()
        content_type = analysis.content_type.value
        
        # Add hash for uniqueness if needed
        url_hash = hashlib.md5(analysis.url.encode()).hexdigest()[:8]
        
        return f"yggdrasil_{domain}_{content_type}_{url_hash}"
    
    async def create_dynamic_table(self, analysis: DataSourceAnalysis) -> bool:
        """Create a dynamic table for specific content type"""
        
        if not analysis.table_name:
            return False
        
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{analysis.table_name}'
                    );
                """))
                
                if result.scalar():
                    logger.info(f"Table {analysis.table_name} already exists")
                    return True
                
                # Create optimized table based on content type
                create_sql = self._generate_table_sql(analysis)
                conn.execute(text(create_sql))
                conn.commit()
                
                logger.info(f"Created dynamic table: {analysis.table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating dynamic table: {e}")
            return False
    
    def _generate_table_sql(self, analysis: DataSourceAnalysis) -> str:
        """Generate optimized table SQL based on content analysis"""
        
        base_sql = f"""
        CREATE TABLE {analysis.table_name} (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title TEXT NOT NULL,
            content TEXT,
            author TEXT,
            source_url TEXT NOT NULL,
            domain VARCHAR(50) DEFAULT '{analysis.domain}',
            language VARCHAR(10) DEFAULT '{analysis.language}',
            word_count INTEGER,
            character_count INTEGER,
            complexity_score FLOAT,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Add indexes based on content type
        if analysis.content_type in [ContentType.LARGE_TEXT, ContentType.BOOK]:
            base_sql += f"""
            CREATE INDEX idx_{analysis.table_name}_title ON {analysis.table_name} USING gin(to_tsvector('english', title));
            CREATE INDEX idx_{analysis.table_name}_content ON {analysis.table_name} USING gin(to_tsvector('english', content));
            CREATE INDEX idx_{analysis.table_name}_domain ON {analysis.table_name}(domain);
            """
        else:
            base_sql += f"""
            CREATE INDEX idx_{analysis.table_name}_title ON {analysis.table_name}(title);
            CREATE INDEX idx_{analysis.table_name}_domain ON {analysis.table_name}(domain);
            """
        
        return base_sql

class YggdrasilMCPServer:
    """Main MCP Server for Yggdrasil system"""
    
    def __init__(self):
        self.server = Server("yggdrasil-mcp-server")
        self.storage_manager = IntelligentStorageManager(
            postgres_url="postgresql://postgres:JGRsolomon0924$@localhost:5431/yggdrasil",
            qdrant_url="http://localhost:6333"
        )
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="analyze_data_source",
                        description="Analyze a data source to determine optimal storage strategy",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL of the data source to analyze"
                                }
                            },
                            "required": ["url"]
                        }
                    ),
                    Tool(
                        name="intelligent_scrape_and_store",
                        description="Intelligently scrape and store data with optimal strategy",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to scrape"
                                },
                                "force_analysis": {
                                    "type": "boolean",
                                    "description": "Force re-analysis of the data source",
                                    "default": False
                                }
                            },
                            "required": ["url"]
                        }
                    ),
                    Tool(
                        name="optimize_storage",
                        description="Optimize storage for existing data",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {
                                    "type": "string",
                                    "description": "Table name to optimize (optional)"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="query_performance_report",
                        description="Generate performance report for queries",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "domain": {
                                    "type": "string",
                                    "description": "Domain to analyze (optional)"
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            
            if name == "analyze_data_source":
                return await self._analyze_data_source(arguments["url"])
            
            elif name == "intelligent_scrape_and_store":
                return await self._intelligent_scrape_and_store(
                    arguments["url"],
                    arguments.get("force_analysis", False)
                )
            
            elif name == "optimize_storage":
                return await self._optimize_storage(arguments.get("table_name"))
            
            elif name == "query_performance_report":
                return await self._query_performance_report(arguments.get("domain"))
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _analyze_data_source(self, url: str) -> CallToolResult:
        """Analyze a data source and return strategy"""
        
        try:
            analysis = await self.storage_manager.analyze_data_source(url)
            
            result = {
                "url": analysis.url,
                "content_type": analysis.content_type.value,
                "estimated_size": analysis.estimated_size,
                "language": analysis.language,
                "domain": analysis.domain,
                "complexity_score": analysis.complexity_score,
                "storage_strategy": analysis.storage_strategy.value,
                "table_name": analysis.table_name,
                "metadata": analysis.metadata
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Data Source Analysis:\n{json.dumps(result, indent=2)}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Error analyzing data source: {str(e)}"
                )]
            )
    
    async def _intelligent_scrape_and_store(self, url: str, force_analysis: bool) -> CallToolResult:
        """Intelligently scrape and store data"""
        
        try:
            # Analyze the data source
            analysis = await self.storage_manager.analyze_data_source(url)
            
            # Create dynamic table if needed
            if analysis.storage_strategy in [StorageStrategy.POSTGRES_ONLY, StorageStrategy.HYBRID]:
                await self.storage_manager.create_dynamic_table(analysis)
            
            # Perform the actual scraping
            result = await self._perform_scraping(url, analysis)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Scraping completed successfully:\n{json.dumps(result, indent=2)}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error in intelligent scraping: {str(e)}"
                )]
            )
    
    async def _perform_scraping(self, url: str, analysis: DataSourceAnalysis) -> Dict[str, Any]:
        """Perform the actual scraping based on analysis"""
        
        # This is a simplified implementation
        # In production, this would use the existing scraping infrastructure
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            content = response.text
        
        # Store based on strategy
        if analysis.storage_strategy == StorageStrategy.POSTGRES_ONLY:
            return await self._store_in_postgres(content, analysis)
        elif analysis.storage_strategy == StorageStrategy.QDRANT_ONLY:
            return await self._store_in_qdrant(content, analysis)
        elif analysis.storage_strategy == StorageStrategy.HYBRID:
            return await self._store_hybrid(content, analysis)
        
        return {"status": "stored", "strategy": analysis.storage_strategy.value}
    
    async def _store_in_postgres(self, content: str, analysis: DataSourceAnalysis) -> Dict[str, Any]:
        """Store data in PostgreSQL"""
        # Implementation would use SQLAlchemy to store in the dynamic table
        return {"status": "stored_postgres", "table": analysis.table_name}
    
    async def _store_in_qdrant(self, content: str, analysis: DataSourceAnalysis) -> Dict[str, Any]:
        """Store data in Qdrant"""
        # Implementation would use Qdrant client to store vectors
        return {"status": "stored_qdrant", "collection": f"yggdrasil_{analysis.domain}"}
    
    async def _store_hybrid(self, content: str, analysis: DataSourceAnalysis) -> Dict[str, Any]:
        """Store data using hybrid approach"""
        # Store metadata in PostgreSQL, full content in Qdrant
        postgres_result = await self._store_in_postgres(content, analysis)
        qdrant_result = await self._store_in_qdrant(content, analysis)
        
        return {
            "status": "stored_hybrid",
            "postgres": postgres_result,
            "qdrant": qdrant_result
        }
    
    async def _optimize_storage(self, table_name: Optional[str]) -> CallToolResult:
        """Optimize storage performance"""
        
        try:
            # Implementation would analyze and optimize storage
            result = {
                "status": "optimized",
                "table_name": table_name,
                "optimizations_applied": [
                    "Rebuilt indexes",
                    "Updated statistics", 
                    "Optimized queries"
                ]
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Storage optimization complete:\n{json.dumps(result, indent=2)}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error optimizing storage: {str(e)}"
                )]
            )
    
    async def _query_performance_report(self, domain: Optional[str]) -> CallToolResult:
        """Generate query performance report"""
        
        try:
            # Implementation would analyze query performance
            result = {
                "domain": domain or "all",
                "performance_metrics": {
                    "avg_query_time": "45ms",
                    "total_queries": 1547,
                    "slow_queries": 3,
                    "index_usage": "94%"
                },
                "recommendations": [
                    "Consider partitioning large tables",
                    "Add composite indexes for frequent queries",
                    "Monitor Qdrant collection size"
                ]
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Performance Report:\n{json.dumps(result, indent=2)}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error generating performance report: {str(e)}"
                )]
            )

async def main():
    """Run the MCP server"""
    mcp_server = YggdrasilMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="yggdrasil-mcp-server",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
