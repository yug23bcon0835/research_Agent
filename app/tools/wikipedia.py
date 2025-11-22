"""Wikipedia search and article retrieval tool."""

import logging
from typing import List, Dict, Any, Optional
import aiohttp
from urllib.parse import quote

logger = logging.getLogger(__name__)


class WikipediaTool:
    """Tool for searching and retrieving Wikipedia articles."""
    
    def __init__(self):
        """Initialize Wikipedia tool."""
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search Wikipedia for articles matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and page ID
        """
        await self._ensure_session()
        
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
                "utf8": 1,
                "formatversion": 2
            }
            
            logger.info(f"Searching Wikipedia for: {query}")
            async with self.session.get(self.base_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get("query", {}).get("search", []):
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": self._clean_html(item.get("snippet", "")),
                            "page_id": item.get("pageid"),
                            "url": f"https://en.wikipedia.org/wiki/{quote(item.get('title', ''))}",
                            "source": "Wikipedia"
                        })
                    
                    logger.info(f"Found {len(results)} Wikipedia results")
                    return results
                else:
                    logger.warning(f"Wikipedia search failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Wikipedia search error: {str(e)}")
            return []
    
    async def get_article_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get the summary/extract of a Wikipedia article.
        
        Args:
            title: Wikipedia article title
            
        Returns:
            Dictionary with article information
        """
        await self._ensure_session()
        
        try:
            params = {
                "action": "query",
                "prop": "extracts|info",
                "exintro": 1,
                "explaintext": 1,
                "titles": title,
                "inprop": "url",
                "format": "json",
                "formatversion": 2
            }
            
            logger.info(f"Fetching Wikipedia article: {title}")
            async with self.session.get(self.base_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get("query", {}).get("pages", [])
                    
                    if pages and len(pages) > 0:
                        page = pages[0]
                        
                        if "missing" in page:
                            logger.warning(f"Wikipedia article not found: {title}")
                            return None
                        
                        return {
                            "title": page.get("title", ""),
                            "extract": page.get("extract", ""),
                            "url": page.get("fullurl", ""),
                            "page_id": page.get("pageid"),
                            "source": "Wikipedia"
                        }
                else:
                    logger.warning(f"Wikipedia article fetch failed with status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Wikipedia article fetch error: {str(e)}")
            return None
    
    async def get_article_sections(self, title: str) -> List[Dict[str, Any]]:
        """
        Get the sections of a Wikipedia article.
        
        Args:
            title: Wikipedia article title
            
        Returns:
            List of sections with their content
        """
        await self._ensure_session()
        
        try:
            params = {
                "action": "parse",
                "page": title,
                "prop": "sections",
                "format": "json",
                "formatversion": 2
            }
            
            logger.info(f"Fetching Wikipedia article sections: {title}")
            async with self.session.get(self.base_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "error" in data:
                        logger.warning(f"Wikipedia article not found: {title}")
                        return []
                    
                    sections = data.get("parse", {}).get("sections", [])
                    
                    return [{
                        "index": section.get("index", ""),
                        "level": section.get("level", 0),
                        "title": section.get("line", ""),
                        "number": section.get("number", "")
                    } for section in sections]
                else:
                    logger.warning(f"Wikipedia sections fetch failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Wikipedia sections fetch error: {str(e)}")
            return []
    
    async def search_and_summarize(self, query: str, max_articles: int = 3) -> List[Dict[str, Any]]:
        """
        Search Wikipedia and get summaries for top results.
        
        Args:
            query: Search query
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of articles with summaries
        """
        search_results = await self.search(query, max_articles)
        
        summaries = []
        for result in search_results:
            summary = await self.get_article_summary(result["title"])
            if summary:
                summaries.append(summary)
        
        return summaries
    
    @staticmethod
    def _clean_html(text: str) -> str:
        """Remove HTML tags from text."""
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
