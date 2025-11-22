"""Multi-agent research coordinator."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.agents.researcher import ResearcherAgent
from app.agents.critic import CriticAgent
from app.agents.reviser import ReviserAgent
from app.database.connection import db_manager
from app.llm.client import llm_client
from app.models.research import (
    ResearchTask,
    ResearchQuery,
    ResearchStatus,
    AgentMessage,
    AgentType
)


class ResearchCoordinator:
    """Coordinates the multi-agent research process with self-correction."""
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.critic = CriticAgent()
        self.reviser = ReviserAgent()
        self.min_quality_score = 7.0  # Minimum acceptable quality score
        self.db_manager = db_manager
        self.llm_client = llm_client
    
    async def initialize(self) -> bool:
        """Initialize the coordinator and all dependencies."""
        try:
            # Initialize LLM client
            llm_initialized = await self.llm_client.initialize()
            if not llm_initialized:
                return False
            
            # Initialize database
            db_result = await self.db_manager.initialize()
            if not db_result.success:
                return False
            
            return True
        except Exception:
            return False
    
    async def conduct_research(self, query: ResearchQuery) -> ResearchTask:
        """Conduct the complete research process with self-correction."""
        
        # Create initial task
        task = ResearchTask(
            query=query,
            status=ResearchStatus.PENDING,
            max_retries=3
        )
        
        # Save task to database
        task_result = await self.db_manager.create_task(task)
        if task_result.success and task_result.data:
            task.id = task_result.data.get("id")
        
        try:
            # Log start of research
            await self._log_agent_message(
                task.id,
                AgentType.RESEARCHER,
                f"Starting research on: {query.topic}"
            )
            
            # Update status to in progress
            await self._update_task_status(task.id, ResearchStatus.IN_PROGRESS)
            
            # Phase 1: Initial Research
            current_report = await self._conduct_initial_research(query, task.id)
            task.current_report = current_report
            
            # Save initial report
            await self.db_manager.save_report(current_report, task.id)

            # Phase 2: Self-Correction Loop
            final_report = await self._self_correction_loop(query, current_report, task.id)
            task.current_report = final_report

            # Save final report
            await self.db_manager.save_report(final_report, task.id)
            
            # Mark task as completed
            await self._update_task_status(task.id, ResearchStatus.COMPLETED)
            task.status = ResearchStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            
            await self._log_agent_message(
                task.id,
                AgentType.RESEARCHER,
                f"Research completed successfully for: {query.topic}"
            )
            
            return task
            
        except Exception as e:
            # Mark task as failed
            await self._update_task_status(task.id, ResearchStatus.FAILED)
            task.status = ResearchStatus.FAILED
            
            await self._log_agent_message(
                task.id,
                AgentType.RESEARCHER,
                f"Research failed: {str(e)}"
            )
            
            raise
    
    async def _conduct_initial_research(self, query: ResearchQuery, task_id: str):
        """Conduct the initial research phase."""
        
        await self._log_agent_message(
            task_id,
            AgentType.RESEARCHER,
            "Conducting initial research..."
        )
        
        # Researcher agent generates initial report
        report = await self.researcher.process(query)
        
        await self._log_agent_message(
            task_id,
            AgentType.RESEARCHER,
            f"Initial research completed. Generated report with {len(report.sections)} sections."
        )
        
        return report
    
    async def _self_correction_loop(self, query: ResearchQuery, initial_report, task_id: str):
        """Run the self-correction loop until quality is acceptable."""
        
        current_report = initial_report
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            # Phase 1: Critique
            await self._update_task_status(task_id, ResearchStatus.REVIEWING)
            
            feedback = await self._critique_report(query, current_report, task_id)
            
            # Check if quality is acceptable
            if feedback.overall_score >= self.min_quality_score:
                await self._log_agent_message(
                    task_id,
                    AgentType.CRITIC,
                    f"Report quality acceptable with score {feedback.overall_score:.1f}. No revisions needed."
                )
                break
            
            # Phase 2: Revise
            await self._update_task_status(task_id, ResearchStatus.REVISING)
            
            current_report = await self._revise_report(query, current_report, feedback, task_id)
            retry_count += 1
            
            await self._log_agent_message(
                task_id,
                AgentType.REVISER,
                f"Revision {retry_count} completed. New report generated."
            )
        
        if retry_count >= max_retries:
            await self._log_agent_message(
                task_id,
                AgentType.RESEARCHER,
                f"Maximum revisions ({max_retries}) reached. Using current report."
            )
        
        return current_report
    
    async def _critique_report(self, query: ResearchQuery, report, task_id: str):
        """Critique the current report."""
        
        await self._log_agent_message(
            task_id,
            AgentType.CRITIC,
            "Analyzing report quality and providing feedback..."
        )
        
        feedback = await self.critic.process(
            query=query,
            context={"report": report}
        )
        
        # Save feedback to database
        await self.db_manager.save_feedback(feedback, task_id)
        
        await self._log_agent_message(
            task_id,
            AgentType.CRITIC,
            f"Critique completed. Overall score: {feedback.overall_score:.1f}/10"
        )
        
        return feedback
    
    async def _revise_report(self, query: ResearchQuery, report, feedback, task_id: str):
        """Revise the report based on feedback."""
        
        await self._log_agent_message(
            task_id,
            AgentType.REVISER,
            "Revising report based on feedback..."
        )
        
        revised_report = await self.reviser.process(
            query=query,
            context={"report": report, "feedback": feedback}
        )
        
        await self._log_agent_message(
            task_id,
            AgentType.REVISER,
            f"Revision completed. Report improved based on {len(feedback.suggestions)} suggestions."
        )
        
        return revised_report
    
    async def _update_task_status(self, task_id: str, status: ResearchStatus):
        """Update the task status in the database."""
        await self.db_manager.update_task(
            task_id=task_id,
            updates={"status": status.value, "updated_at": datetime.now(timezone.utc).isoformat()}
        )
    
    async def _log_agent_message(self, task_id: str, agent_type: AgentType, message: str):
        """Log an agent message to the database."""
        agent_message = AgentMessage(
            agent_type=agent_type,
            message=message,
            timestamp=datetime.now(timezone.utc)
        )

        await self.db_manager.log_agent_message(agent_message, task_id)
    
    async def get_task_status(self, task_id: str) -> Optional[ResearchTask]:
        """Get the current status of a research task."""
        result = await self.db_manager.get_task(task_id)
        if result.success and result.data:
            return ResearchTask(**result.data)
        return None
