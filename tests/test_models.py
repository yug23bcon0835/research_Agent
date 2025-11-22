"""Tests for Pydantic models."""

import pytest
from datetime import datetime
from app.models.research import (
    ResearchQuery,
    ResearchReport,
    ResearchSection,
    ResearchSource,
    CritiqueFeedback,
    AgentMessage,
    AgentType,
    ResearchStatus
)


class TestResearchQuery:
    """Test ResearchQuery model."""
    
    def test_valid_query(self):
        """Test creating a valid research query."""
        query = ResearchQuery(
            topic="Artificial Intelligence",
            subtopics=["Machine Learning", "Neural Networks"],
            depth_level=3
        )
        
        assert query.topic == "Artificial Intelligence"
        assert len(query.subtopics) == 2
        assert query.depth_level == 3
    
    def test_invalid_depth_level(self):
        """Test validation of depth level."""
        with pytest.raises(ValueError):
            ResearchQuery(topic="Test", depth_level=0)
        
        with pytest.raises(ValueError):
            ResearchQuery(topic="Test", depth_level=6)


class TestResearchSource:
    """Test ResearchSource model."""
    
    def test_valid_source(self):
        """Test creating a valid research source."""
        source = ResearchSource(
            title="AI Research Paper",
            url="https://example.com/paper",
            content="Summary of the research paper",
            credibility_score=0.9
        )
        
        assert source.title == "AI Research Paper"
        assert source.credibility_score == 0.9
    
    def test_invalid_credibility_score(self):
        """Test validation of credibility score."""
        with pytest.raises(ValueError):
            ResearchSource(
                title="Test",
                content="Test content",
                credibility_score=1.5  # Too high
            )
        
        with pytest.raises(ValueError):
            ResearchSource(
                title="Test",
                content="Test content",
                credibility_score=-0.1  # Too low
            )


class TestResearchSection:
    """Test ResearchSection model."""
    
    def test_valid_section(self):
        """Test creating a valid research section."""
        source = ResearchSource(
            title="Test Source",
            content="Test content",
            credibility_score=0.8
        )
        
        section = ResearchSection(
            title="Introduction",
            content="This is the introduction",
            sources=[source],
            confidence_score=0.9
        )
        
        assert section.title == "Introduction"
        assert len(section.sources) == 1
        assert section.confidence_score == 0.9


class TestResearchReport:
    """Test ResearchReport model."""
    
    def test_valid_report(self):
        """Test creating a valid research report."""
        source = ResearchSource(
            title="Test Source",
            content="Test content",
            credibility_score=0.8
        )
        
        section = ResearchSection(
            title="Introduction",
            content="This is the introduction",
            sources=[source],
            confidence_score=0.9
        )
        
        report = ResearchReport(
            title="AI Research Report",
            abstract="This is the abstract",
            sections=[section],
            conclusion="This is the conclusion",
            sources=[source]
        )
        
        assert report.title == "AI Research Report"
        assert len(report.sections) == 1
        assert len(report.sources) == 1


class TestCritiqueFeedback:
    """Test CritiqueFeedback model."""
    
    def test_valid_feedback(self):
        """Test creating valid critique feedback."""
        feedback = CritiqueFeedback(
            overall_score=8.5,
            strengths=["Well structured", "Good sources"],
            weaknesses=["Needs more depth"],
            suggestions=["Add more examples"],
            specific_corrections={"abstract": "Make it more concise"},
            priority_issues=["Add recent sources"]
        )
        
        assert feedback.overall_score == 8.5
        assert len(feedback.strengths) == 2
        assert len(feedback.weaknesses) == 1
    
    def test_invalid_score(self):
        """Test validation of overall score."""
        with pytest.raises(ValueError):
            CritiqueFeedback(
                overall_score=11.0,  # Too high
                strengths=[],
                weaknesses=[],
                suggestions=[]
            )
        
        with pytest.raises(ValueError):
            CritiqueFeedback(
                overall_score=-1.0,  # Too low
                strengths=[],
                weaknesses=[],
                suggestions=[]
            )


class TestAgentMessage:
    """Test AgentMessage model."""
    
    def test_valid_message(self):
        """Test creating a valid agent message."""
        message = AgentMessage(
            agent_type=AgentType.RESEARCHER,
            message="Research started",
            metadata={"task_id": "123"}
        )
        
        assert message.agent_type == AgentType.RESEARCHER
        assert message.message == "Research started"
        assert isinstance(message.timestamp, datetime)
