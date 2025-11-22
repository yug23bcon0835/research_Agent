"""Critic agent for evaluating research reports."""

import json
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent
from app.models.research import (
    AgentType,
    ResearchQuery,
    ResearchReport,
    CritiqueFeedback
)


class CriticAgent(BaseAgent):
    """Agent responsible for critiquing research reports and providing feedback."""
    
    def __init__(self):
        super().__init__(AgentType.CRITIC)
    
    async def process(
        self,
        query: ResearchQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> CritiqueFeedback:
        """Process the research report and provide critique feedback."""
        
        if not context or "report" not in context:
            raise ValueError("Critic agent requires a report in the context")
        
        report = context["report"]
        
        system_prompt = """You are an expert research critic with extensive experience in evaluating academic and professional research. 
        Your role is to provide constructive, detailed feedback on research reports. Be thorough but fair, 
        and focus on helping improve the quality of the research.

        Evaluate the report on these criteria:
        1. Accuracy and factual correctness
        2. Depth and comprehensiveness
        3. Logical structure and coherence
        4. Quality and relevance of sources
        5. Objectivity and bias
        6. Clarity and readability
        7. Completeness relative to the research query
        """
        
        # Generate critique feedback
        feedback = await self._generate_critique(query, report, system_prompt)
        
        # Create structured feedback
        critique_feedback = CritiqueFeedback(
            overall_score=feedback.get("overall_score", 5.0),
            strengths=feedback.get("strengths", []),
            weaknesses=feedback.get("weaknesses", []),
            suggestions=feedback.get("suggestions", []),
            specific_corrections=feedback.get("specific_corrections", {}),
            priority_issues=feedback.get("priority_issues", [])
        )
        
        return critique_feedback
    
    async def _generate_critique(
        self,
        query: ResearchQuery,
        report: ResearchReport,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Generate detailed critique feedback for the report."""
        
        # Convert report to text for analysis
        report_text = self._report_to_text(report)
        
        prompt = f"""
        Please provide a comprehensive critique of the following research report:
        
        Research Query:
        Topic: {query.topic}
        Subtopics: {', '.join(query.subtopics) if query.subtopics else 'None specified'}
        Depth Level: {query.depth_level}
        Requirements: {query.requirements or 'None specified'}
        
        Research Report:
        Title: {report.title}
        Abstract: {report.abstract}
        
        Sections:
        {self._sections_to_text(report.sections)}
        
        Conclusion: {report.conclusion}
        
        Number of Sources: {len(report.sources)}
        
        Provide your critique as a JSON object with the following structure:
        {{
            "overall_score": 7.5,
            "strengths": [
                "Well-structured report with clear sections",
                "Good use of credible sources",
                "Comprehensive coverage of the topic"
            ],
            "weaknesses": [
                "Some sections lack sufficient depth",
                "Limited analysis of conflicting viewpoints",
                "Conclusion could be more detailed"
            ],
            "suggestions": [
                "Expand the analysis section with more detailed examples",
                "Include counterarguments and address them",
                "Add more recent sources to strengthen the research"
            ],
            "specific_corrections": {{
                "abstract": "Make the abstract more concise and focused on key findings",
                "section_2": "This section needs more statistical evidence",
                "conclusion": "Add specific recommendations for future research"
            }},
            "priority_issues": [
                "Add more recent and diverse sources",
                "Address potential bias in the analysis",
                "Strengthen the connection between research questions and conclusions"
            ]
        }}
        
        Scoring Guidelines:
        - 9.0-10.0: Excellent, publication-ready quality
        - 8.0-8.9: Very good, minor improvements needed
        - 7.0-7.9: Good, moderate improvements needed
        - 6.0-6.9: Acceptable, significant improvements needed
        - 5.0-5.9: Needs major improvements
        - Below 5.0: Requires complete revision
        
        Be specific and constructive in your feedback.
        """
        
        response = await self.generate_structured_llm_response(prompt, system_prompt)
        return response
    
    def _report_to_text(self, report: ResearchReport) -> str:
        """Convert report to text for analysis."""
        text = f"Title: {report.title}\n\n"
        text += f"Abstract: {report.abstract}\n\n"
        
        text += "Sections:\n"
        for i, section in enumerate(report.sections, 1):
            text += f"\n{i}. {section.title}\n"
            text += f"{section.content}\n"
        
        text += f"\nConclusion: {report.conclusion}\n"
        text += f"\nSources: {len(report.sources)} sources referenced"
        
        return text
    
    def _sections_to_text(self, sections: List) -> str:
        """Convert sections to text format."""
        text = ""
        for i, section in enumerate(sections, 1):
            text += f"\n{i}. {section.title}\n"
            text += f"{section.content}\n"
            text += f"Sources in this section: {len(section.sources)}\n"
        return text
