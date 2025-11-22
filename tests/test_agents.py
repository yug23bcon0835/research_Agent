"""Tests for agent implementations."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.researcher import ResearcherAgent
from app.agents.critic import CriticAgent
from app.agents.reviser import ReviserAgent
from app.models.research import (
    ResearchQuery,
    ResearchReport,
    CritiqueFeedback,
    ResearchSection,
    ResearchSource
)


class TestResearcherAgent:
    """Test ResearcherAgent."""
    
    @pytest.fixture
    def researcher(self):
        """Create a researcher agent instance."""
        return ResearcherAgent()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query."""
        return ResearchQuery(
            topic="Artificial Intelligence",
            subtopics=["Machine Learning"],
            depth_level=3
        )
    
    @pytest.mark.asyncio
    async def test_process_research(self, researcher, sample_query):
        """Test the research process."""
        # Mock LLM responses
        mock_plan_response = {
            "key_areas": ["AI fundamentals", "ML algorithms"],
            "source_types": ["academic", "industry"],
            "report_structure": ["intro", "analysis", "conclusion"],
            "research_questions": ["What is AI?"],
            "challenges": ["Complexity"]
        }
        
        mock_report_response = {
            "abstract": "Test abstract",
            "sections": [
                {
                    "title": "Introduction",
                    "content": "Test content",
                    "sources": [
                        {
                            "title": "Test Source",
                            "url": "https://example.com",
                            "content": "Test source content",
                            "credibility_score": 0.9
                        }
                    ],
                    "confidence_score": 0.8
                }
            ],
            "conclusion": "Test conclusion",
            "sources": [
                {
                    "title": "Test Source",
                    "url": "https://example.com",
                    "content": "Test source content",
                    "credibility_score": 0.9
                }
            ]
        }
        
        with patch.object(researcher, 'generate_structured_llm_response') as mock_llm:
            mock_llm.side_effect = [mock_plan_response, mock_report_response]
            
            report = await researcher.process(sample_query)
            
            assert isinstance(report, ResearchReport)
            assert report.title == "Research Report: Artificial Intelligence"
            assert report.abstract == "Test abstract"
            assert len(report.sections) == 1
            assert report.sections[0].title == "Introduction"
            assert len(report.sources) == 1


class TestCriticAgent:
    """Test CriticAgent."""
    
    @pytest.fixture
    def critic(self):
        """Create a critic agent instance."""
        return CriticAgent()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query."""
        return ResearchQuery(
            topic="Artificial Intelligence",
            depth_level=3
        )
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample research report."""
        source = ResearchSource(
            title="Test Source",
            content="Test content",
            credibility_score=0.8
        )
        
        section = ResearchSection(
            title="Introduction",
            content="Test section content",
            sources=[source],
            confidence_score=0.8
        )
        
        return ResearchReport(
            title="Test Report",
            abstract="Test abstract",
            sections=[section],
            conclusion="Test conclusion",
            sources=[source]
        )
    
    @pytest.mark.asyncio
    async def test_process_critique(self, critic, sample_query, sample_report):
        """Test the critique process."""
        mock_feedback_response = {
            "overall_score": 7.5,
            "strengths": ["Good structure", "Clear content"],
            "weaknesses": ["Needs more depth"],
            "suggestions": ["Add more examples"],
            "specific_corrections": {"abstract": "Make it more concise"},
            "priority_issues": ["Add recent sources"]
        }
        
        with patch.object(critic, 'generate_structured_llm_response') as mock_llm:
            mock_llm.return_value = mock_feedback_response
            
            feedback = await critic.process(
                sample_query,
                context={"report": sample_report}
            )
            
            assert isinstance(feedback, CritiqueFeedback)
            assert feedback.overall_score == 7.5
            assert len(feedback.strengths) == 2
            assert len(feedback.weaknesses) == 1
            assert "abstract" in feedback.specific_corrections
    
    @pytest.mark.asyncio
    async def test_process_missing_context(self, critic, sample_query):
        """Test critique process with missing context."""
        with pytest.raises(ValueError, match="Critic agent requires a report in the context"):
            await critic.process(sample_query)


class TestReviserAgent:
    """Test ReviserAgent."""
    
    @pytest.fixture
    def reviser(self):
        """Create a reviser agent instance."""
        return ReviserAgent()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query."""
        return ResearchQuery(
            topic="Artificial Intelligence",
            depth_level=3
        )
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample research report."""
        source = ResearchSource(
            title="Test Source",
            content="Test content",
            credibility_score=0.8
        )
        
        section = ResearchSection(
            title="Introduction",
            content="Test section content",
            sources=[source],
            confidence_score=0.8
        )
        
        return ResearchReport(
            title="Test Report",
            abstract="Test abstract",
            sections=[section],
            conclusion="Test conclusion",
            sources=[source]
        )
    
    @pytest.fixture
    def sample_feedback(self):
        """Create sample critique feedback."""
        return CritiqueFeedback(
            overall_score=6.5,
            strengths=["Good structure"],
            weaknesses=["Needs more depth"],
            suggestions=["Add more examples"],
            specific_corrections={"abstract": "Make it more concise"},
            priority_issues=["Add recent sources"]
        )
    
    @pytest.mark.asyncio
    async def test_process_revision(self, reviser, sample_query, sample_report, sample_feedback):
        """Test the revision process."""
        mock_revised_response = {
            "title": "Revised: Test Report",
            "abstract": "Revised abstract",
            "sections": [
                {
                    "title": "Revised Introduction",
                    "content": "Revised content with more depth",
                    "sources": [
                        {
                            "title": "New Source",
                            "url": "https://example.com/new",
                            "content": "New source content",
                            "credibility_score": 0.9
                        }
                    ],
                    "confidence_score": 0.9
                }
            ],
            "conclusion": "Revised conclusion",
            "sources": [
                {
                    "title": "New Source",
                    "url": "https://example.com/new",
                    "content": "New source content",
                    "credibility_score": 0.9
                }
            ],
            "revision_summary": "Improved depth and added recent sources"
        }
        
        with patch.object(reviser, 'generate_structured_llm_response') as mock_llm:
            mock_llm.return_value = mock_revised_response
            
            revised_report = await reviser.process(
                sample_query,
                context={"report": sample_report, "feedback": sample_feedback}
            )
            
            assert isinstance(revised_report, ResearchReport)
            assert revised_report.title == "Revised: Test Report"
            assert revised_report.abstract == "Revised abstract"
            assert len(revised_report.sections) == 1
            assert revised_report.sections[0].title == "Revised Introduction"
            assert revised_report.sections[0].confidence_score == 0.9
    
    @pytest.mark.asyncio
    async def test_process_missing_context(self, reviser, sample_query):
        """Test revision process with missing context."""
        with pytest.raises(ValueError, match="Reviser agent requires context with report and feedback"):
            await reviser.process(sample_query)
        
        with pytest.raises(ValueError, match="Reviser agent requires both report and feedback in context"):
            await reviser.process(sample_query, context={"report": "test"})
