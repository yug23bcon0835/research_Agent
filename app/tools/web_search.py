"""Web search tool using DuckDuckGo and optional premium APIs."""

import logging
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Tool for searching the web using various search engines."""
    
    def __init__(self, tavily_api_key: Optional[str] = None, serpapi_key: Optional[str] = None):
        """Initialize web search tool with optional API keys."""
        self.tavily_api_key = tavily_api_key
        self.serpapi_key = serpapi_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo Instant Answer API.
        
        Note: This is a simple implementation. For production, consider using
        duckduckgo-search library or paid API for better results.
        """
        await self._ensure_session()
        
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            logger.info(f"Searching DuckDuckGo for: {query}")
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    # Extract relevant results
                    if data.get("AbstractText"):
                        results.append({
                            "title": data.get("Heading", query),
                            "snippet": data.get("AbstractText", ""),
                            "url": data.get("AbstractURL", ""),
                            "source": "DuckDuckGo"
                        })
                    
                    # Add related topics
                    for topic in data.get("RelatedTopics", [])[:max_results-1]:
                        if isinstance(topic, dict) and "Text" in topic:
                            results.append({
                                "title": topic.get("Text", "")[:100],
                                "snippet": topic.get("Text", ""),
                                "url": topic.get("FirstURL", ""),
                                "source": "DuckDuckGo"
                            })
                    
                    logger.info(f"Found {len(results)} results from DuckDuckGo")
                    return results[:max_results]
                else:
                    logger.warning(f"DuckDuckGo search failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    async def search_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Tavily AI Search API (premium, better quality results)."""
        if not self.tavily_api_key:
            logger.debug("Tavily API key not configured, skipping")
            return []
        
        await self._ensure_session()
        
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False
            }
            
            logger.info(f"Searching Tavily for: {query}")
            async with self.session.post(url, json=payload, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get("results", [])[:max_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("content", ""),
                            "url": item.get("url", ""),
                            "score": item.get("score", 0.0),
                            "source": "Tavily"
                        })
                    
                    logger.info(f"Found {len(results)} results from Tavily")
                    return results
                else:
                    logger.warning(f"Tavily search failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using available search engines.
        Tries premium APIs first, falls back to free alternatives.
        """
        results = []
        
        # Try Tavily first if available (better quality)
        if self.tavily_api_key:
            results = await self.search_tavily(query, max_results)
            if results:
                return results
        
        # Fall back to DuckDuckGo
        results = await self.search_duckduckgo(query, max_results)
        
        if not results:
            logger.warning(f"No search results found for query: {query}")
            # Return a placeholder result to avoid empty results
            results = [{
                "title": f"Search: {query}",
                "snippet": "No web results found. This is a placeholder for demonstration.",
                "url": "https://example.com",
                "source": "Placeholder"
            }]
        
        return results
    
    async def multi_query_search(self, queries: List[str], max_results_per_query: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Execute multiple search queries concurrently."""
        tasks = [self.search(query, max_results_per_query) for query in queries]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        results_dict = {}
        for query, results in zip(queries, results_list):
            if isinstance(results, Exception):
                logger.error(f"Error searching for '{query}': {str(results)}")
                results_dict[query] = []
            else:
                results_dict[query] = results
        
        return results_dict
