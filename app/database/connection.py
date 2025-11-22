"""Supabase database connection and operations."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from supabase import create_client, Client
from app.config import settings
from app.models.research import (
    DatabaseOperationResult,
    ResearchTask,
    ResearchReport,
    CritiqueFeedback,
    AgentMessage
)


class SupabaseManager:
    """Manages Supabase database operations."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialized = False
    
    async def initialize(self) -> DatabaseOperationResult:
        """Initialize Supabase client."""
        try:
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            self._initialized = True
            return DatabaseOperationResult(
                success=True,
                message="Supabase client initialized successfully",
                data={"client_initialized": True}
            )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Failed to initialize Supabase client",
                error=str(e)
            )
    
    def _ensure_initialized(self):
        """Ensure database client is initialized."""
        if not self._initialized or not self.client:
            raise RuntimeError("Database client not initialized. Call initialize() first.")
    
    async def create_task(self, task: ResearchTask) -> DatabaseOperationResult:
        """Create a new research task."""
        self._ensure_initialized()
        
        try:
            task_data = task.model_dump(exclude_none=True)
            task_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.client.table("research_tasks").insert(task_data).execute()
            
            if response.data:
                return DatabaseOperationResult(
                    success=True,
                    message="Task created successfully",
                    data=response.data[0] if response.data else None
                )
            else:
                return DatabaseOperationResult(
                    success=False,
                    message="Failed to create task",
                    error="No data returned from database"
                )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Database error while creating task",
                error=str(e)
            )
    
    async def get_task(self, task_id: str) -> DatabaseOperationResult:
        """Get a research task by ID."""
        self._ensure_initialized()
        
        try:
            response = self.client.table("research_tasks").select("*").eq("id", task_id).execute()
            
            if response.data:
                return DatabaseOperationResult(
                    success=True,
                    message="Task retrieved successfully",
                    data=response.data[0] if response.data else None
                )
            else:
                return DatabaseOperationResult(
                    success=False,
                    message="Task not found",
                    error=f"No task found with ID: {task_id}"
                )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Database error while retrieving task",
                error=str(e)
            )
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> DatabaseOperationResult:
        """Update a research task."""
        self._ensure_initialized()
        
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            response = self.client.table("research_tasks").update(updates).eq("id", task_id).execute()
            
            if response.data:
                return DatabaseOperationResult(
                    success=True,
                    message="Task updated successfully",
                    data=response.data[0] if response.data else None
                )
            else:
                return DatabaseOperationResult(
                    success=False,
                    message="Failed to update task",
                    error="No data returned from database"
                )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Database error while updating task",
                error=str(e)
            )
    
    async def save_report(self, report: ResearchReport, task_id: str) -> DatabaseOperationResult:
        """Save a research report."""
        self._ensure_initialized()
        
        try:
            report_data = report.model_dump(exclude_none=True)
            report_data["task_id"] = task_id
            report_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.client.table("research_reports").insert(report_data).execute()
            
            if response.data:
                return DatabaseOperationResult(
                    success=True,
                    message="Report saved successfully",
                    data=response.data[0] if response.data else None
                )
            else:
                return DatabaseOperationResult(
                    success=False,
                    message="Failed to save report",
                    error="No data returned from database"
                )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Database error while saving report",
                error=str(e)
            )
    
    async def save_feedback(self, feedback: CritiqueFeedback, task_id: str) -> DatabaseOperationResult:
        """Save critique feedback."""
        self._ensure_initialized()
        
        try:
            feedback_data = feedback.model_dump(exclude_none=True)
            feedback_data["task_id"] = task_id
            feedback_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.client.table("critique_feedback").insert(feedback_data).execute()
            
            if response.data:
                return DatabaseOperationResult(
                    success=True,
                    message="Feedback saved successfully",
                    data=response.data[0] if response.data else None
                )
            else:
                return DatabaseOperationResult(
                    success=False,
                    message="Failed to save feedback",
                    error="No data returned from database"
                )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Database error while saving feedback",
                error=str(e)
            )
    
    async def log_agent_message(self, message: AgentMessage, task_id: str) -> DatabaseOperationResult:
        """Log an agent message."""
        self._ensure_initialized()
        
        try:
            message_data = message.model_dump(exclude_none=True)
            message_data["task_id"] = task_id
            
            response = self.client.table("agent_messages").insert(message_data).execute()
            
            if response.data:
                return DatabaseOperationResult(
                    success=True,
                    message="Agent message logged successfully",
                    data=response.data[0] if response.data else None
                )
            else:
                return DatabaseOperationResult(
                    success=False,
                    message="Failed to log agent message",
                    error="No data returned from database"
                )
        except Exception as e:
            return DatabaseOperationResult(
                success=False,
                message="Database error while logging agent message",
                error=str(e)
            )


# Global database manager instance
db_manager = SupabaseManager()
