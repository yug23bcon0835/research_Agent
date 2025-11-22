"""arXiv research paper search tool."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


class ArxivTool:
    """Tool for searching and retrieving research papers from arXiv."""
    
    def __init__(self):
        """Initialize arXiv tool."""
        self.base_url = "http://export.arxiv.org/api/query"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        sort_by: str = "relevance",
        sort_order: str = "descending"
    ) -> List[Dict[str, Any]]:
        """
        Search arXiv for research papers.
        
        Args:
            query: Search query (can use field prefixes like 'ti:', 'au:', 'abs:', 'cat:')
            max_results: Maximum number of results to return
            sort_by: Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate'
            sort_order: 'ascending' or 'descending'
            
        Returns:
            List of paper results
        """
        await self._ensure_session()
        
        try:
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": sort_by,
                "sortOrder": sort_order
            }
            
            logger.info(f"Searching arXiv for: {query}")
            async with self.session.get(self.base_url, params=params, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    results = self._parse_arxiv_response(content)
                    logger.info(f"Found {len(results)} arXiv papers")
                    return results
                else:
                    logger.warning(f"arXiv search failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"arXiv search error: {str(e)}")
            return []
    
    async def search_by_category(
        self,
        category: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search arXiv by category.
        
        Args:
            category: arXiv category (e.g., 'cs.AI', 'physics.comp-ph', 'math.CO')
            max_results: Maximum number of results
            
        Returns:
            List of paper results
        """
        query = f"cat:{category}"
        return await self.search(query, max_results, sort_by="submittedDate")
    
    async def search_by_author(
        self,
        author: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search arXiv by author.
        
        Args:
            author: Author name
            max_results: Maximum number of results
            
        Returns:
            List of paper results
        """
        query = f"au:{author}"
        return await self.search(query, max_results)
    
    async def search_by_title(
        self,
        title: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search arXiv by title.
        
        Args:
            title: Paper title or keywords
            max_results: Maximum number of results
            
        Returns:
            List of paper results
        """
        query = f"ti:{title}"
        return await self.search(query, max_results)
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv API XML response."""
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            results = []
            
            for entry in root.findall('atom:entry', namespaces):
                # Extract basic information
                paper_id = entry.find('atom:id', namespaces)
                title = entry.find('atom:title', namespaces)
                summary = entry.find('atom:summary', namespaces)
                published = entry.find('atom:published', namespaces)
                updated = entry.find('atom:updated', namespaces)
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    name = author.find('atom:name', namespaces)
                    if name is not None and name.text:
                        authors.append(name.text)
                
                # Extract categories
                categories = []
                for category in entry.findall('atom:category', namespaces):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                
                # Extract links
                pdf_link = None
                abs_link = None
                for link in entry.findall('atom:link', namespaces):
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                    elif link.get('rel') == 'alternate':
                        abs_link = link.get('href')
                
                paper = {
                    "id": paper_id.text if paper_id is not None else "",
                    "title": self._clean_text(title.text if title is not None else ""),
                    "abstract": self._clean_text(summary.text if summary is not None else ""),
                    "authors": authors,
                    "categories": categories,
                    "published": published.text if published is not None else "",
                    "updated": updated.text if updated is not None else "",
                    "pdf_url": pdf_link,
                    "url": abs_link or (paper_id.text if paper_id is not None else ""),
                    "source": "arXiv"
                }
                
                results.append(paper)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {str(e)}")
            return []
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text by removing extra whitespace."""
        import re
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    async def get_paper_details(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific paper.
        
        Args:
            arxiv_id: arXiv ID (e.g., '2301.12345' or 'http://arxiv.org/abs/2301.12345')
            
        Returns:
            Paper details
        """
        # Extract just the ID if a full URL was provided
        if 'arxiv.org' in arxiv_id:
            arxiv_id = arxiv_id.split('/')[-1]
        
        query = f"id:{arxiv_id}"
        results = await self.search(query, max_results=1)
        
        return results[0] if results else None
