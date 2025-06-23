"""Academic content scraper for research papers, journals, and educational content."""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ScrapedText
from ..database.enhanced_models import ContentType, KnowledgeDomain, Language

@dataclass
class AcademicPaper:
    """Represents an academic paper."""
    title: str
    authors: List[str]
    abstract: str
    content: str
    journal: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    publication_date: Optional[datetime] = None
    keywords: List[str] = None
    domain: KnowledgeDomain = KnowledgeDomain.SCIENCE

class AcademicScraper(BaseScraper):
    """Scraper for academic content from various sources."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        
    async def scrape_arxiv_paper(self, arxiv_id: str) -> AcademicPaper:
        """Scrape a paper from arXiv."""
        
        # Get paper metadata from arXiv API
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        async with self.session.get(api_url) as response:
            xml_content = await response.text()
            
            # Parse XML for metadata
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_content)
            
            entry = root.find('{http://www.w3.org/2005/Atom}entry')
            if not entry:
                raise ValueError(f"arXiv paper {arxiv_id} not found")
            
            # Extract metadata
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name = author.find('{http://www.w3.org/2005/Atom}name').text
                authors.append(name)
            
            abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            
            # Get publication date
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            
            # Get categories for domain classification
            categories = [cat.attrib['term'] for cat in entry.findall('{http://arxiv.org/schemas/atom}category')]
            domain = self._categorize_arxiv_paper(categories)
            
            # Get PDF content (this would require additional processing)
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            content = f"Abstract: {abstract}\n\n[Full PDF available at: {pdf_url}]"
            
            return AcademicPaper(
                title=title,
                authors=authors,
                abstract=abstract,
                content=content,
                arxiv_id=arxiv_id,
                publication_date=pub_date,
                keywords=categories,
                domain=domain
            )
    
    async def scrape_wikipedia_category(self, category: str, limit: int = 10) -> List[ScrapedText]:
        """Scrape articles from a Wikipedia category."""
        
        # Get articles in category
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/list/{category}"
        
        try:
            async with self.session.get(api_url) as response:
                if response.status_code == 404:
                    # Try alternate API
                    alt_url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{category}&format=json&cmlimit={limit}"
                    async with self.session.get(alt_url) as alt_response:
                        data = await alt_response.json()
                        articles = data.get('query', {}).get('categorymembers', [])
                else:
                    data = await response.json()
                    articles = data.get('items', [])[:limit]
            
            scraped_texts = []
            
            for article in articles:
                try:
                    title = article.get('title', article.get('title', ''))
                    if not title:
                        continue
                    
                    # Scrape individual article
                    article_content = await self._scrape_wikipedia_article(title)
                    if article_content:
                        scraped_texts.append(article_content)
                        
                except Exception as e:
                    self.logger.warning(f"Error scraping Wikipedia article {title}: {e}")
                    continue
            
            return scraped_texts
            
        except Exception as e:
            self.logger.error(f"Error scraping Wikipedia category {category}: {e}")
            return []
    
    async def _scrape_wikipedia_article(self, title: str) -> Optional[ScrapedText]:
        """Scrape a single Wikipedia article."""
        
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        
        try:
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                
                # Get main content
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if not content_div:
                    return None
                
                # Remove unwanted elements
                for element in content_div.find_all(['table', 'div'], 
                                                   class_=re.compile('infobox|navbox|references|hatnote')):
                    element.decompose()
                
                # Extract paragraphs
                paragraphs = content_div.find_all('p')
                content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                if len(content) < 100:  # Skip very short articles
                    return None
                
                return ScrapedText(
                    title=title,
                    content=content,
                    text_type=ContentType.WIKIPEDIA,
                    language=Language.ENGLISH,
                    source_url=url,
                    author="Wikipedia Contributors",
                    metadata={
                        "domain": self._categorize_content(content),
                        "word_count": len(content.split()),
                        "scraped_at": datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error scraping Wikipedia article {title}: {e}")
            return None
    
    async def scrape_stanford_encyclopedia(self, topic: str) -> Optional[ScrapedText]:
        """Scrape an entry from Stanford Encyclopedia of Philosophy."""
        
        # Search for the topic
        search_url = f"https://plato.stanford.edu/search/searcher.py?query={topic}"
        
        try:
            async with self.session.get(search_url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                
                # Find first result link
                result_link = soup.find('a', href=re.compile(r'/entries/'))
                if not result_link:
                    return None
                
                entry_url = f"https://plato.stanford.edu{result_link['href']}"
                
                # Scrape the actual entry
                async with self.session.get(entry_url) as entry_response:
                    entry_soup = BeautifulSoup(await entry_response.text(), 'html.parser')
                    
                    # Get title
                    title_elem = entry_soup.find('h1')
                    title = title_elem.get_text().strip() if title_elem else topic
                    
                    # Get content
                    content_div = entry_soup.find('div', {'id': 'main-text'})
                    if not content_div:
                        content_div = entry_soup.find('div', {'id': 'article'})
                    
                    if content_div:
                        # Remove bibliography and notes
                        for element in content_div.find_all(['div'], 
                                                           class_=re.compile('bibliography|notes')):
                            element.decompose()
                        
                        content = content_div.get_text()
                        content = re.sub(r'\n\s*\n', '\n\n', content)  # Clean up whitespace
                        
                        return ScrapedText(
                            title=title,
                            content=content,
                            text_type=ContentType.PHILOSOPHY_TEXT,
                            language=Language.ENGLISH,
                            source_url=entry_url,
                            author="Stanford Encyclopedia of Philosophy",
                            metadata={
                                "domain": KnowledgeDomain.PHILOSOPHY,
                                "word_count": len(content.split()),
                                "scraped_at": datetime.now().isoformat()
                            }
                        )
                        
        except Exception as e:
            self.logger.error(f"Error scraping Stanford Encyclopedia entry for {topic}: {e}")
            return None
    
    def _categorize_arxiv_paper(self, categories: List[str]) -> KnowledgeDomain:
        """Categorize arXiv paper by subject categories."""
        
        category_mapping = {
            'cs.': KnowledgeDomain.TECHNOLOGY,
            'math.': KnowledgeDomain.MATHEMATICS,
            'physics.': KnowledgeDomain.SCIENCE,
            'q-bio.': KnowledgeDomain.MEDICINE,
            'econ.': KnowledgeDomain.ECONOMICS,
            'stat.': KnowledgeDomain.MATHEMATICS
        }
        
        for category in categories:
            for prefix, domain in category_mapping.items():
                if category.startswith(prefix):
                    return domain
        
        return KnowledgeDomain.SCIENCE  # Default for academic papers
    
    def _categorize_content(self, content: str) -> str:
        """Categorize content by keywords."""
        
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['philosophy', 'philosopher', 'philosophical']):
            return KnowledgeDomain.PHILOSOPHY
        elif any(term in content_lower for term in ['science', 'scientific', 'research']):
            return KnowledgeDomain.SCIENCE
        elif any(term in content_lower for term in ['mathematics', 'mathematical', 'theorem']):
            return KnowledgeDomain.MATHEMATICS
        elif any(term in content_lower for term in ['history', 'historical', 'century']):
            return KnowledgeDomain.HISTORY
        elif any(term in content_lower for term in ['literature', 'literary', 'author']):
            return KnowledgeDomain.LITERATURE
        else:
            return KnowledgeDomain.OTHER
    
    async def scrape(self) -> List[ScrapedText]:
        """Override base scrape method."""
        # This would be implemented based on configuration
        return []
