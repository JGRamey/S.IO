"""Text sourcing agent for finding and validating spiritual texts."""

import asyncio
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from langchain.schema import HumanMessage, SystemMessage

from yggdrasil.config import settings
from yggdrasil.database.models import TextType, Language
from .base import BaseAgent, AgentResult


class TextSourcingAgent(BaseAgent):
    """Agent for sourcing and validating spiritual texts from various sources."""
    
    TRUSTED_SOURCES = {
        "sacred-texts.com": {"reliability": 0.9, "type": "archive"},
        "gutenberg.org": {"reliability": 0.95, "type": "archive"},
        "blueletterbible.org": {"reliability": 0.85, "type": "bible"},
        "perseus.tufts.edu": {"reliability": 0.9, "type": "classical"},
        "vatican.va": {"reliability": 0.95, "type": "catholic"},
        "jewishvirtuallibrary.org": {"reliability": 0.8, "type": "jewish"},
        "quran.com": {"reliability": 0.9, "type": "islamic"},
    }
    
    def __init__(self):
        super().__init__(
            name="text_sourcing",
            description="Sources and validates spiritual texts from trusted archives"
        )
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute text sourcing based on input parameters."""
        try:
            query = input_data.get("query", "")
            text_type = input_data.get("text_type")
            language = input_data.get("language")
            sources = input_data.get("sources", [])
            
            if not query:
                return self._create_result(
                    success=False,
                    error="Query parameter is required"
                )
            
            # Search for texts
            search_results = await self._search_texts(query, text_type, language, sources)
            
            # Validate and score results
            validated_results = await self._validate_sources(search_results)
            
            return self._create_result(
                success=True,
                data={
                    "query": query,
                    "results": validated_results,
                    "total_found": len(validated_results)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Text sourcing failed: {e}")
            return self._create_result(
                success=False,
                error=str(e)
            )
    
    async def _search_texts(
        self,
        query: str,
        text_type: Optional[str] = None,
        language: Optional[str] = None,
        sources: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for texts across multiple sources."""
        results = []
        
        # If specific sources provided, use them; otherwise use all trusted sources
        search_sources = sources or list(self.TRUSTED_SOURCES.keys())
        
        tasks = []
        for source in search_sources:
            if source in self.TRUSTED_SOURCES:
                task = self._search_single_source(source, query, text_type, language)
                tasks.append(task)
        
        # Execute searches concurrently
        source_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in source_results:
            if isinstance(result, Exception):
                self.logger.warning(f"Search failed for source: {result}")
                continue
            if result:
                results.extend(result)
        
        return results
    
    async def _search_single_source(
        self,
        source: str,
        query: str,
        text_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search a single source for texts."""
        try:
            # Customize search based on source
            if source == "sacred-texts.com":
                return await self._search_sacred_texts(query, text_type, language)
            elif source == "blueletterbible.org":
                return await self._search_blue_letter_bible(query, language)
            elif source == "gutenberg.org":
                return await self._search_gutenberg(query, text_type)
            else:
                # Generic web search for other sources
                return await self._generic_web_search(source, query)
                
        except Exception as e:
            self.logger.error(f"Search failed for {source}: {e}")
            return []
    
    async def _search_sacred_texts(
        self,
        query: str,
        text_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search sacred-texts.com."""
        base_url = "https://sacred-texts.com"
        search_url = f"{base_url}/search.htm"
        
        try:
            response = await self.http_client.get(
                search_url,
                params={"q": query}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse search results (this would need to be customized based on actual HTML structure)
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.startswith('/'):
                    full_url = urljoin(base_url, href)
                    title = link.get_text(strip=True)
                    
                    if title and len(title) > 10:  # Filter out short/empty titles
                        results.append({
                            "title": title,
                            "url": full_url,
                            "source": "sacred-texts.com",
                            "text_type": self._infer_text_type(title, href),
                            "language": self._infer_language(title, href),
                        })
            
            return results[:10]  # Limit results
            
        except Exception as e:
            self.logger.error(f"Sacred-texts search failed: {e}")
            return []
    
    async def _search_blue_letter_bible(
        self,
        query: str,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search Blue Letter Bible."""
        # This would implement specific search logic for Blue Letter Bible
        # For now, return empty list as placeholder
        return []
    
    async def _search_gutenberg(
        self,
        query: str,
        text_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search Project Gutenberg."""
        # This would implement specific search logic for Project Gutenberg
        # For now, return empty list as placeholder
        return []
    
    async def _generic_web_search(
        self,
        source: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """Generic web search for a source."""
        # This would implement a generic web search strategy
        # For now, return empty list as placeholder
        return []
    
    async def _validate_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and score source reliability."""
        validated = []
        
        for result in results:
            source_domain = urlparse(result["url"]).netloc.lower()
            
            # Find matching trusted source
            reliability_score = 0.5  # Default
            for trusted_source, info in self.TRUSTED_SOURCES.items():
                if trusted_source in source_domain:
                    reliability_score = info["reliability"]
                    break
            
            # Use LLM to assess content quality
            content_score = await self._assess_content_quality(result)
            
            # Combine scores
            final_score = (reliability_score + content_score) / 2
            
            result["reliability_score"] = reliability_score
            result["content_score"] = content_score
            result["final_score"] = final_score
            result["validated_at"] = datetime.now().isoformat()
            
            validated.append(result)
        
        # Sort by final score
        validated.sort(key=lambda x: x["final_score"], reverse=True)
        return validated
    
    async def _assess_content_quality(self, result: Dict[str, Any]) -> float:
        """Use LLM to assess content quality."""
        try:
            # Fetch a sample of the content
            sample_content = await self._fetch_content_sample(result["url"])
            
            if not sample_content:
                return 0.3
            
            system_prompt = """You are an expert in spiritual and religious texts. 
            Assess the quality and authenticity of the provided text sample.
            Consider factors like:
            - Scholarly accuracy
            - Translation quality
            - Historical authenticity
            - Completeness
            - Proper attribution
            
            Respond with a score from 0.0 to 1.0, where 1.0 is highest quality."""
            
            analysis_prompt = f"""Assess this text sample for quality and authenticity:
            
            Title: {result.get('title', 'Unknown')}
            Source: {result.get('source', 'Unknown')}
            
            Sample content:
            {sample_content[:1000]}...
            
            Provide only a numeric score between 0.0 and 1.0."""
            
            response = await self._analyze_text(sample_content, analysis_prompt, system_prompt)
            
            # Extract numeric score from response
            score_match = re.search(r'(\d+\.?\d*)', response)
            if score_match:
                score = float(score_match.group(1))
                return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
            
            return 0.5  # Default if no score found
            
        except Exception as e:
            self.logger.error(f"Content quality assessment failed: {e}")
            return 0.3
    
    async def _fetch_content_sample(self, url: str) -> Optional[str]:
        """Fetch a sample of content from URL."""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:2000]  # Return first 2000 characters
            
        except Exception as e:
            self.logger.error(f"Failed to fetch content from {url}: {e}")
            return None
    
    def _infer_text_type(self, title: str, url: str) -> Optional[str]:
        """Infer text type from title and URL."""
        title_lower = title.lower()
        url_lower = url.lower()
        
        if any(word in title_lower for word in ["bible", "gospel", "testament"]):
            return TextType.BIBLE.value
        elif any(word in title_lower for word in ["quran", "koran"]):
            return TextType.QURAN.value
        elif any(word in title_lower for word in ["torah", "talmud"]):
            return TextType.TORAH.value
        elif any(word in title_lower for word in ["upanishad", "vedas"]):
            return TextType.UPANISHADS.value
        elif "bhagavad" in title_lower:
            return TextType.BHAGAVAD_GITA.value
        elif "tao" in title_lower:
            return TextType.TAO_TE_CHING.value
        elif "dhamma" in title_lower:
            return TextType.DHAMMAPADA.value
        elif "gnostic" in title_lower:
            return TextType.GNOSTIC.value
        elif "zohar" in title_lower:
            return TextType.ZOHAR.value
        
        return TextType.OTHER.value
    
    def _infer_language(self, title: str, url: str) -> Optional[str]:
        """Infer language from title and URL."""
        title_lower = title.lower()
        url_lower = url.lower()
        
        if any(word in title_lower for word in ["hebrew", "עברית"]):
            return Language.HEBREW.value
        elif any(word in title_lower for word in ["greek", "ελληνικά"]):
            return Language.GREEK.value
        elif any(word in title_lower for word in ["latin", "latina"]):
            return Language.LATIN.value
        elif any(word in title_lower for word in ["arabic", "عربي"]):
            return Language.ARABIC.value
        elif any(word in title_lower for word in ["sanskrit", "संस्कृत"]):
            return Language.SANSKRIT.value
        elif any(word in title_lower for word in ["aramaic"]):
            return Language.ARAMAIC.value
        
        return Language.ENGLISH.value  # Default to English
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
