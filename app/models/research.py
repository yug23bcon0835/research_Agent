"""Research-related Pydantic models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class AgentType(str, Enum):
    """Agent types in the system."""
    RESEARCHER = "researcher"
    CRITIC = "critic"
    REVISER = "reviser"


class ResearchStatus(str, Enum):
    """Research task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEWING = "reviewing"
    REVISING = "revising"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchQuery(BaseModel):
    """Research query model."""
    
    topic: str = Field(..., description="Main research topic")
    subtopics: List[str] = Field(default_factory=list, description="Subtopics to explore")
    depth_level: int = Field(default=3, ge=1, le=5, description="Research depth level")
    requirements: Optional[str] = Field(None, description="Specific requirements for the research")
    
    @field_validator('depth_level')
    @classmethod
    def validate_depth(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Depth level must be between 1 and 5')
        return v


class ResearchSource(BaseModel):
    """Research source model."""
    
    title: str = Field(..., description="Source title")
    url: Optional[str] = Field(None, description="Source URL")
    content: str = Field(..., description="Source content summary")
    credibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Source credibility score")
    publication_date: Optional[datetime] = Field(None, description="Publication date")


class ResearchSection(BaseModel):
    """Research section model."""
    
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    sources: List[ResearchSource] = Field(default_factory=list, description="Sources used in this section")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in this section")


class ResearchReport(BaseModel):
    """Complete research report model."""
    
    id: Optional[str] = Field(None, description="Report ID")
    title: str = Field(..., description="Report title")
    abstract: str = Field(..., description="Report abstract")
    sections: List[ResearchSection] = Field(default_factory=list, description="Report sections")
    conclusion: str = Field(..., description="Report conclusion")
    sources: List[ResearchSource] = Field(default_factory=list, description="All sources used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class AgentMessage(BaseModel):
    """Agent communication message model."""
    
    agent_type: AgentType = Field(..., description="Type of agent sending the message")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")


class CritiqueFeedback(BaseModel):
    """Critique feedback model."""
    
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall quality score")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    specific_corrections: Dict[str, str] = Field(default_factory=dict, description="Specific corrections needed")
    priority_issues: List[str] = Field(default_factory=list, description="High priority issues to address")


class ResearchTask(BaseModel):
    """Research task model for tracking progress."""
    
    id: Optional[str] = Field(None, description="Task ID")
    query: ResearchQuery = Field(..., description="Research query")
    status: ResearchStatus = Field(default=ResearchStatus.PENDING, description="Task status")
    current_report: Optional[ResearchReport] = Field(None, description="Current report version")
    feedback_history: List[CritiqueFeedback] = Field(default_factory=list, description="Feedback history")
    agent_messages: List[AgentMessage] = Field(default_factory=list, description="Agent communication log")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    max_retries: int = Field(default=3, description="Maximum allowed retries")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class DatabaseOperationResult(BaseModel):
    """Result of database operations."""
    
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Result message")
    data: Optional[Any] = Field(None, description="Returned data")
    error: Optional[str] = Field(None, description="Error details if failed")
