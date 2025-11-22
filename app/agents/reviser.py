"""Reviser agent for improving research reports based on feedback."""

import json
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent
from app.models.research import (
    AgentType,
    ResearchQuery,
    ResearchReport,
    CritiqueFeedback,
    ResearchSection,
    ResearchSource
)


class ReviserAgent(BaseAgent):
    """Agent responsible for revising research reports based on critique feedback."""
    
    def __init__(self):
        super().__init__(AgentType.REVISER)
    
    async def process(
        self,
        query: ResearchQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> ResearchReport:
        """Process the research report and feedback to create an improved version."""
        
        if not context:
            raise ValueError("Reviser agent requires context with report and feedback")
        
        report = context.get("report")
        feedback = context.get("feedback")
        
        if not report or not feedback:
            raise ValueError("Reviser agent requires both report and feedback in context")
        
        system_prompt = """You are an expert editor and reviser with extensive experience in improving research reports. 
        Your task is to revise research reports based on detailed feedback, addressing all identified issues 
        while maintaining the core content and strengthening the overall quality.

        Follow these principles:
        1. Address all feedback points systematically
        2. Maintain factual accuracy and objectivity
        3. Improve clarity, coherence, and structure
        4. Enhance source quality and diversity
        5. Strengthen arguments and analysis
        6. Preserve the original research intent
        7. Ensure logical flow and readability
        """
        
        # Generate revised report
        revised_report = await self._generate_revised_report(query, report, feedback, system_prompt)
        
        return revised_report
    
    async def _generate_revised_report(
        self,
        query: ResearchQuery,
        original_report: ResearchReport,
        feedback: CritiqueFeedback,
        system_prompt: str
    ) -> ResearchReport:
        """Generate a revised version of the research report."""
        
        prompt = f"""
        Please revise the following research report based on the detailed feedback provided:
        
        Original Research Query:
        Topic: {query.topic}
        Subtopics: {', '.join(query.subtopics) if query.subtopics else 'None specified'}
        Depth Level: {query.depth_level}
        Requirements: {query.requirements or 'None specified'}
        
        Original Report:
        Title: {original_report.title}
        Abstract: {original_report.abstract}
        
        Sections:
        {self._sections_to_text(original_report.sections)}
        
        Conclusion: {original_report.conclusion}
        
        Critique Feedback:
        Overall Score: {feedback.overall_score}/10
        
        Strengths:
        {chr(10).join(f"- {strength}" for strength in feedback.strengths)}
        
        Weaknesses:
        {chr(10).join(f"- {weakness}" for weakness in feedback.weaknesses)}
        
        Suggestions:
        {chr(10).join(f"- {suggestion}" for suggestion in feedback.suggestions)}
        
        Specific Corrections:
        {chr(10).join(f"- {section}: {correction}" for section, correction in feedback.specific_corrections.items())}
        
        Priority Issues:
        {chr(10).join(f"- {issue}" for issue in feedback.priority_issues)}
        
        Please create a revised report that addresses all the feedback. Return your response as a JSON object:
        {{
            "title": "Revised Report Title",
            "abstract": "Revised abstract text...",
            "sections": [
                {{
                    "title": "Revised Section Title",
                    "content": "Revised section content with improvements...",
                    "sources": [
                        {{
                            "title": "Source Title",
                            "url": "https://example.com/source",
                            "content": "Brief summary of source content",
                            "credibility_score": 0.9
                        }}
                    ],
                    "confidence_score": 0.9
                }}
            ],
            "conclusion": "Revised conclusion text...",
            "sources": [
                {{
                    "title": "Source Title",
                    "url": "https://example.com/source",
                    "content": "Brief summary",
                    "credibility_score": 0.9
                }}
            ],
            "revision_summary": "Summary of key improvements made"
        }}
        
        Focus on:
        1. Addressing all weaknesses and priority issues
        2. Implementing specific corrections
        3. Incorporating suggestions for improvement
        4. Maintaining and enhancing the strengths
        5. Adding better and more diverse sources
        6. Improving overall quality and coherence
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
                confidence_score=section_data.get("confidence_score", 0.8)
            ))
        
        sources = []
        for source_data in response.get("sources", []):
            sources.append(ResearchSource(**source_data))
        
        # Create revised report with metadata
        revised_report = ResearchReport(
            title=response.get("title", f"Revised: {original_report.title}"),
            abstract=response.get("abstract", ""),
            sections=sections,
            conclusion=response.get("conclusion", ""),
            sources=sources,
            metadata={
                **original_report.metadata,
                "revision_summary": response.get("revision_summary", ""),
                "original_feedback_score": feedback.overall_score,
                "revision_number": original_report.metadata.get("revision_number", 0) + 1,
                "revision_timestamp": json.dumps({"timestamp": "now"})  # Simplified
            }
        )
        
        return revised_report
    
    def _sections_to_text(self, sections: List) -> str:
        """Convert sections to text format."""
        text = ""
        for i, section in enumerate(sections, 1):
            text += f"\n{i}. {section.title}\n"
            text += f"{section.content}\n"
            text += f"Confidence Score: {section.confidence_score}\n"
            text += f"Sources in this section: {len(section.sources)}\n"
        return text
