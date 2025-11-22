"""Base agent class for all research agents."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.llm.client import llm_client
from app.models.research import (
    AgentMessage,
    AgentType,
    ResearchQuery,
    ResearchReport,
    CritiqueFeedback
)


class BaseAgent(ABC):
    """Base class for all research agents."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.llm_client = llm_client
    
    @abstractmethod
    async def process(
        self,
        query: ResearchQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Process the research query."""
        pass
    
    async def generate_llm_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM."""
        return await self.llm_client.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
    
    async def generate_structured_llm_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Generate a structured JSON response from the LLM."""
        return await self.llm_client.generate_structured_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
    
    def create_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> AgentMessage:
        """Create an agent message."""
        return AgentMessage(
            agent_type=self.agent_type,
            message=message,
            metadata=metadata or {}
        )
