"""Researcher agent for conducting initial research."""

import json
import logging
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent
from app.models.research import (
    AgentType,
    ResearchQuery,
    ResearchReport,
    ResearchSection,
    ResearchSource
)
from app.tools.web_search import WebSearchTool
from app.tools.wikipedia import WikipediaTool
from app.tools.arxiv_search import ArxivTool
from app.config import settings

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Agent responsible for conducting initial research and generating reports."""
    
    def __init__(self):
        super().__init__(AgentType.RESEARCHER)
        # Initialize research tools
        self.web_search = WebSearchTool(
            tavily_api_key=settings.tavily_api_key,
            serpapi_key=settings.serpapi_key
        )
        self.wikipedia = WikipediaTool()
        self.arxiv = ArxivTool()
    
    async def process(
        self,
        query: ResearchQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> ResearchReport:
        """Process the research query and generate an initial report."""
        
        system_prompt = """You are an expert researcher with deep knowledge across multiple domains. 
        Your task is to conduct comprehensive research on the given topic and generate a detailed, 
        well-structured research report. Follow these guidelines:

        1. Provide accurate, factual information
        2. Use credible sources and cite them properly
        3. Structure the report with clear sections
        4. Include relevant data and examples
        5. Maintain objectivity and avoid bias
        6. Consider multiple perspectives
        7. Ensure logical flow and coherence
        """
        
        # Step 1: Gather real research data from external sources
        logger.info(f"Gathering research data for topic: {query.topic}")
        research_data = await self._gather_research_data(query)
        
        # Step 2: Generate research plan
        research_plan = await self._generate_research_plan(query, system_prompt)
        
        # Step 3: Generate report content with real data
        report_content = await self._generate_report_content(query, research_plan, research_data, system_prompt)
        
        # Create the research report
        report = ResearchReport(
            title=f"Research Report: {query.topic}",
            abstract=report_content.get("abstract", ""),
            sections=report_content.get("sections", []),
            conclusion=report_content.get("conclusion", ""),
            sources=report_content.get("sources", []),
            metadata={
                "depth_level": query.depth_level,
                "subtopics_explored": query.subtopics,
                "research_plan": research_plan,
                "sources_gathered": {
                    "web": len(research_data.get("web_results", [])),
                    "wikipedia": len(research_data.get("wikipedia_results", [])),
                    "arxiv": len(research_data.get("arxiv_results", []))
                }
            }
        )
        
        # Cleanup tool sessions
        await self.web_search.close()
        await self.wikipedia.close()
        await self.arxiv.close()
        
        return report
    
    async def _gather_research_data(self, query: ResearchQuery) -> Dict[str, Any]:
        """Gather research data from multiple sources."""
        research_data = {
            "web_results": [],
            "wikipedia_results": [],
            "arxiv_results": []
        }
        
        try:
            # Search web for main topic and subtopics
            search_queries = [query.topic] + (query.subtopics or [])
            logger.info(f"Searching web for queries: {search_queries}")
            
            web_results = await self.web_search.multi_query_search(search_queries, max_results_per_query=3)
            research_data["web_results"] = [
                result
                for results_list in web_results.values()
                for result in results_list
            ]
            logger.info(f"Gathered {len(research_data['web_results'])} web results")
            
            # Search Wikipedia for main topic
            logger.info(f"Searching Wikipedia for: {query.topic}")
            wiki_results = await self.wikipedia.search_and_summarize(query.topic, max_articles=3)
            research_data["wikipedia_results"] = wiki_results
            logger.info(f"Gathered {len(wiki_results)} Wikipedia articles")
            
            # Search arXiv for academic papers (if topic seems academic)
            logger.info(f"Searching arXiv for: {query.topic}")
            arxiv_results = await self.arxiv.search(query.topic, max_results=5)
            research_data["arxiv_results"] = arxiv_results
            logger.info(f"Gathered {len(arxiv_results)} arXiv papers")
            
        except Exception as e:
            logger.error(f"Error gathering research data: {str(e)}", exc_info=True)
        
        return research_data
    
    async def _generate_research_plan(self, query: ResearchQuery, system_prompt: str) -> Dict[str, Any]:
        """Generate a research plan for the given query."""
        
        prompt = f"""
        Create a comprehensive research plan for the following topic:
        
        Topic: {query.topic}
        Subtopics: {', '.join(query.subtopics) if query.subtopics else 'None specified'}
        Depth Level: {query.depth_level} (1-5, where 5 is most detailed)
        Requirements: {query.requirements or 'None specified'}
        
        Your research plan should include:
        1. Key areas to investigate
        2. Types of sources to consult
        3. Structure for the final report
        4. Specific questions to answer
        5. Potential challenges and how to address them
        
        Return your response as a JSON object with the following structure:
        {{
            "key_areas": ["area1", "area2", ...],
            "source_types": ["academic", "industry_reports", "news", ...],
            "report_structure": ["introduction", "background", "analysis", "conclusion"],
            "research_questions": ["question1", "question2", ...],
            "challenges": ["challenge1", "challenge2", ...]
        }}
        """
        
        response = await self.generate_structured_llm_response(prompt, system_prompt)
        return response
    
    async def _generate_report_content(
        self,
        query: ResearchQuery,
        research_plan: Dict[str, Any],
        research_data: Dict[str, Any],
        system_prompt: str
    ) -> Dict[str, Any]:
        """Generate the actual report content."""
        
        # Format research data for the LLM
        research_context = self._format_research_data(research_data)
        
        prompt = f"""
        Based on the research plan and the gathered research data, generate a comprehensive research report on:
        
        Topic: {query.topic}
        Subtopics: {', '.join(query.subtopics) if query.subtopics else 'None specified'}
        Depth Level: {query.depth_level}
        Requirements: {query.requirements or 'None specified'}
        
        Research Plan:
        {json.dumps(research_plan, indent=2)}
        
        Research Data Gathered:
        {research_context}
        
        Generate a detailed research report with the following structure:
        
        1. Abstract: A concise summary of the entire report (150-200 words)
        2. Sections: Multiple well-structured sections covering different aspects
        3. Conclusion: Key findings and implications
        
        For each section, include:
        - Clear title
        - Comprehensive content synthesized from the research data
        - Relevant sources from the gathered research data (use real URLs and titles from the data provided)
        
        Important: Use the actual sources provided in the research data. Reference web articles, Wikipedia pages,
        and arXiv papers by their real titles and URLs. Give proper attribution to sources.
        
        Return your response as a JSON object with this structure:
        {{
            "abstract": "Abstract text here...",
            "sections": [
                {{
                    "title": "Section Title",
                    "content": "Section content here based on research data...",
                    "sources": [
                        {{
                            "title": "Actual source title from research data",
                            "url": "Actual URL from research data",
                            "content": "Brief summary of source content",
                            "credibility_score": 0.9
                        }}
                    ],
                    "confidence_score": 0.8
                }}
            ],
            "conclusion": "Conclusion text here based on findings...",
            "sources": [
                {{
                    "title": "Actual source title from research data",
                    "url": "Actual URL from research data",
                    "content": "Brief summary",
                    "credibility_score": 0.9
                }}
            ]
        }}
        
        Make sure the content is detailed, well-researched, and professional in tone.
        Base your report on the actual research data provided, not on fictional sources.
        """
        
        response = await self.generate_structured_llm_response(prompt, system_prompt)
        
        # Convert dictionaries to proper model objects
        sections = []
        for section_data in response.get("sections", []):
            sources = []
            for source_data in section_data.get("sources", []):
                sources.append(ResearchSource(**source_data))
            
            sections.append(ResearchSection(
                title=section_data.get("title", ""),
                content=section_data.get("content", ""),
                sources=sources,
                confidence_score=section_data.get("confidence_score", 0.7)
            ))
        
        sources = []
        for source_data in response.get("sources", []):
            sources.append(ResearchSource(**source_data))
        
        return {
            "abstract": response.get("abstract", ""),
            "sections": sections,
            "conclusion": response.get("conclusion", ""),
            "sources": sources
        }
    
    def _format_research_data(self, research_data: Dict[str, Any]) -> str:
        """Format research data into a readable string for the LLM."""
        formatted = []
        
        # Format web results
        web_results = research_data.get("web_results", [])
        if web_results:
            formatted.append("=== WEB SEARCH RESULTS ===")
            for i, result in enumerate(web_results[:10], 1):
                formatted.append(f"\n{i}. {result.get('title', 'No title')}")
                formatted.append(f"   URL: {result.get('url', 'No URL')}")
                formatted.append(f"   Snippet: {result.get('snippet', 'No snippet')[:200]}")
        
        # Format Wikipedia results
        wiki_results = research_data.get("wikipedia_results", [])
        if wiki_results:
            formatted.append("\n\n=== WIKIPEDIA ARTICLES ===")
            for i, result in enumerate(wiki_results, 1):
                formatted.append(f"\n{i}. {result.get('title', 'No title')}")
                formatted.append(f"   URL: {result.get('url', 'No URL')}")
                formatted.append(f"   Extract: {result.get('extract', 'No extract')[:500]}")
        
        # Format arXiv results
        arxiv_results = research_data.get("arxiv_results", [])
        if arxiv_results:
            formatted.append("\n\n=== ARXIV RESEARCH PAPERS ===")
            for i, result in enumerate(arxiv_results, 1):
                formatted.append(f"\n{i}. {result.get('title', 'No title')}")
                formatted.append(f"   Authors: {', '.join(result.get('authors', []))}")
                formatted.append(f"   URL: {result.get('url', 'No URL')}")
                formatted.append(f"   Abstract: {result.get('abstract', 'No abstract')[:300]}")
        
        if not formatted:
            return "No research data gathered."
        
        return "\n".join(formatted)
