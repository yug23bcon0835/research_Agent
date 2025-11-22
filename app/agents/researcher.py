"""Researcher agent for conducting initial research."""

import json
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent
from app.models.research import (
    AgentType,
    ResearchQuery,
    ResearchReport,
    ResearchSection,
    ResearchSource
)


class ResearcherAgent(BaseAgent):
    """Agent responsible for conducting initial research and generating reports."""
    
    def __init__(self):
        super().__init__(AgentType.RESEARCHER)
    
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
        
        # Generate research plan
        research_plan = await self._generate_research_plan(query, system_prompt)
        
        # Generate report content
        report_content = await self._generate_report_content(query, research_plan, system_prompt)
        
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
                "research_plan": research_plan
            }
        )
        
        return report
    
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
        system_prompt: str
    ) -> Dict[str, Any]:
        """Generate the actual report content."""
        
        prompt = f"""
        Based on the research plan, generate a comprehensive research report on:
        
        Topic: {query.topic}
        Subtopics: {', '.join(query.subtopics) if query.subtopics else 'None specified'}
        Depth Level: {query.depth_level}
        Requirements: {query.requirements or 'None specified'}
        
        Research Plan:
        {json.dumps(research_plan, indent=2)}
        
        Generate a detailed research report with the following structure:
        
        1. Abstract: A concise summary of the entire report (150-200 words)
        2. Sections: Multiple well-structured sections covering different aspects
        3. Conclusion: Key findings and implications
        
        For each section, include:
        - Clear title
        - Comprehensive content
        - Relevant sources (create realistic but fictional sources for demonstration)
        
        Return your response as a JSON object with this structure:
        {{
            "abstract": "Abstract text here...",
            "sections": [
                {{
                    "title": "Section Title",
                    "content": "Section content here...",
                    "sources": [
                        {{
                            "title": "Source Title",
                            "url": "https://example.com/source",
                            "content": "Brief summary of source content",
                            "credibility_score": 0.9
                        }}
                    ],
                    "confidence_score": 0.8
                }}
            ],
            "conclusion": "Conclusion text here...",
            "sources": [
                {{
                    "title": "Source Title",
                    "url": "https://example.com/source",
                    "content": "Brief summary",
                    "credibility_score": 0.9
                }}
            ]
        }}
        
        Make sure the content is detailed, well-researched, and professional in tone.
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
