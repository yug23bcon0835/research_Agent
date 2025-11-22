"""FastAPI routes for the research application."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from app.orchestrator.coordinator import ResearchCoordinator
from app.models.research import ResearchQuery, ResearchTask, ResearchStatus


# Pydantic models for API requests/responses
class ResearchRequest(BaseModel):
    """Research request model."""
    topic: str
    subtopics: List[str] = []
    depth_level: int = 3
    requirements: Optional[str] = None


class ResearchResponse(BaseModel):
    """Research response model."""
    task_id: str
    status: str
    message: str
    created_at: datetime


class TaskStatusResponse(BaseModel):
    """Task status response model."""
    task_id: str
    status: str
    progress: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Research API",
    description="Self-correcting multi-agent research application",
    version="1.0.0"
)

# Global coordinator instance
coordinator = ResearchCoordinator()


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    success = await coordinator.initialize()
    if not success:
        raise RuntimeError("Failed to initialize application")


@app.post("/research", response_model=ResearchResponse)
async def create_research_task(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
) -> ResearchResponse:
    """Create a new research task."""
    
    try:
        # Create research query
        query = ResearchQuery(
            topic=request.topic,
            subtopics=request.subtopics,
            depth_level=request.depth_level,
            requirements=request.requirements
        )
        
        # Start research in background
        background_tasks.add_task(coordinator.conduct_research, query)
        
        # Create initial task record
        task = ResearchTask(
            query=query,
            status=ResearchStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        # Save task to database
        task_result = await coordinator.conduct_research(query)
        
        return ResearchResponse(
            task_id=task_result.id or "unknown",
            status=task_result.status.value,
            message="Research task created successfully",
            created_at=task_result.created_at or datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create research task: {str(e)}")


@app.get("/research/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get the status of a research task."""
    
    try:
        task = await coordinator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskStatusResponse(
            task_id=task.id or task_id,
            status=task.status.value,
            progress={
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "has_report": task.current_report is not None,
                "feedback_count": len(task.feedback_history),
                "message_count": len(task.agent_messages)
            },
            created_at=task.created_at or datetime.utcnow(),
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@app.get("/research/{task_id}/report")
async def get_research_report(task_id: str):
    """Get the final research report for a task."""
    
    try:
        task = await coordinator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.status != ResearchStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Task not completed yet")
        
        if not task.current_report:
            raise HTTPException(status_code=404, detail="No report available")
        
        return task.current_report.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research report: {str(e)}")


@app.get("/research/{task_id}/messages")
async def get_agent_messages(task_id: str):
    """Get all agent messages for a task."""
    
    try:
        task = await coordinator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        messages = [msg.dict() for msg in task.agent_messages]
        
        return {
            "task_id": task_id,
            "message_count": len(messages),
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent messages: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Research API",
        "version": "1.0.0",
        "endpoints": {
            "create_research": "POST /research",
            "get_status": "GET /research/{task_id}/status",
            "get_report": "GET /research/{task_id}/report",
            "get_messages": "GET /research/{task_id}/messages",
            "health": "GET /health"
        }
    }
