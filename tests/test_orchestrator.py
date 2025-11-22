"""Tests for the orchestrator coordinator."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.orchestrator.coordinator import ResearchCoordinator
from app.models.research import (
    ResearchQuery,
    ResearchTask,
    ResearchStatus,
    ResearchReport,
    CritiqueFeedback,
    AgentType
)


class TestResearchCoordinator:
    """Test ResearchCoordinator."""
    
    @pytest.fixture
    def coordinator(self):
        """Create a coordinator instance."""
        return ResearchCoordinator()
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample research query."""
        return ResearchQuery(
            topic="Artificial Intelligence",
            subtopics=["Machine Learning"],
            depth_level=3
        )
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample research report."""
        from app.models.research import ResearchSection, ResearchSource
        
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
            overall_score=8.5,  # High score to skip revisions
            strengths=["Good structure", "Clear content"],
            weaknesses=[],
            suggestions=[],
            specific_corrections={},
            priority_issues=[]
        )
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, coordinator):
        """Test successful initialization."""
        with patch.object(coordinator.researcher.llm_client, 'initialize') as mock_llm_init, \
             patch.object(coordinator.db_manager, 'initialize') as mock_db_init:
            
            mock_llm_init.return_value = True
            mock_db_init.return_value = MagicMock(success=True)
            
            result = await coordinator.initialize()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, coordinator):
        """Test initialization failure."""
        with patch.object(coordinator.researcher.llm_client, 'initialize') as mock_llm_init:
            mock_llm_init.return_value = False
            
            result = await coordinator.initialize()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_conduct_research_success(self, coordinator, sample_query, sample_report, sample_feedback):
        """Test successful research conduction."""
        # Mock all dependencies
        mock_db_manager = MagicMock()
        mock_db_manager.create_task = AsyncMock(return_value=MagicMock(success=True, data={"id": "task123"}))
        mock_db_manager.save_report = AsyncMock()
        mock_db_manager.update_task = AsyncMock()
        mock_db_manager.log_agent_message = AsyncMock()

        with patch.object(coordinator, 'db_manager', mock_db_manager), \
             patch.object(coordinator, 'initialize') as mock_init, \
             patch.object(coordinator, '_conduct_initial_research') as mock_research, \
             patch.object(coordinator, '_self_correction_loop') as mock_correction:

            # Setup mocks
            mock_init.return_value = True
            mock_research.return_value = sample_report
            mock_correction.return_value = sample_report
            mock_feedback = sample_feedback

            with patch.object(coordinator, '_critique_report', return_value=mock_feedback):
                task = await coordinator.conduct_research(sample_query)

            assert isinstance(task, ResearchTask)
            assert task.query == sample_query
            assert task.status == ResearchStatus.COMPLETED
            assert task.current_report == sample_report
    
    @pytest.mark.asyncio
    async def test_conduct_initial_research(self, coordinator, sample_query, sample_report):
        """Test initial research phase."""
        mock_db_manager = MagicMock()
        mock_db_manager.save_report = AsyncMock()
        mock_db_manager.log_agent_message = AsyncMock()

        with patch.object(coordinator, 'db_manager', mock_db_manager), \
             patch.object(coordinator.researcher, 'process') as mock_research_process:

            mock_research_process.return_value = sample_report

            result = await coordinator._conduct_initial_research(sample_query, "task123")

            assert result == sample_report
            mock_research_process.assert_called_once_with(sample_query)
    
    @pytest.mark.asyncio
    async def test_self_correction_loop_high_quality(self, coordinator, sample_query, sample_report, sample_feedback):
        """Test self-correction loop with high quality (no revisions needed)."""
        mock_db_manager = MagicMock()
        mock_db_manager.update_task = AsyncMock()
        mock_db_manager.log_agent_message = AsyncMock()

        with patch.object(coordinator, 'db_manager', mock_db_manager), \
             patch.object(coordinator, '_critique_report') as mock_critique, \
             patch.object(coordinator, '_revise_report') as mock_revise:

            mock_critique.return_value = sample_feedback  # High score

            result = await coordinator._self_correction_loop(sample_query, sample_report, "task123")

            assert result == sample_report
            mock_critique.assert_called_once()
            mock_revise.assert_not_called()  # No revisions needed
    
    @pytest.mark.asyncio
    async def test_self_correction_loop_with_revisions(self, coordinator, sample_query, sample_report):
        """Test self-correction loop with revisions needed."""
        # Create low-quality feedback to trigger revisions
        low_quality_feedback = CritiqueFeedback(
            overall_score=6.0,  # Low score to trigger revision
            strengths=["Some structure"],
            weaknesses=["Needs more depth"],
            suggestions=["Add more content"],
            specific_corrections={"abstract": "Improve abstract"},
            priority_issues=["Add sources"]
        )

        # Create high-quality feedback for final iteration
        high_quality_feedback = CritiqueFeedback(
            overall_score=8.5,  # High score to end revisions
            strengths=["Good structure", "Clear content"],
            weaknesses=[],
            suggestions=[],
            specific_corrections={},
            priority_issues=[]
        )

        # Create revised report
        revised_report = sample_report
        revised_report.title = "Revised Report"

        mock_db_manager = MagicMock()
        mock_db_manager.update_task = AsyncMock()
        mock_db_manager.log_agent_message = AsyncMock()

        with patch.object(coordinator, 'db_manager', mock_db_manager), \
             patch.object(coordinator, '_critique_report') as mock_critique, \
             patch.object(coordinator, '_revise_report') as mock_revise:

            # First critique returns low score, second returns high score
            mock_critique.side_effect = [low_quality_feedback, high_quality_feedback]
            mock_revise.return_value = revised_report

            result = await coordinator._self_correction_loop(sample_query, sample_report, "task123")

            assert result == revised_report
            assert mock_critique.call_count == 2
            mock_revise.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_critique_report(self, coordinator, sample_query, sample_report, sample_feedback):
        """Test report critique."""
        mock_db_manager = MagicMock()
        mock_db_manager.save_feedback = AsyncMock()
        mock_db_manager.log_agent_message = AsyncMock()

        with patch.object(coordinator, 'db_manager', mock_db_manager), \
             patch.object(coordinator.critic, 'process') as mock_critique_process:

            mock_critique_process.return_value = sample_feedback

            result = await coordinator._critique_report(sample_query, sample_report, "task123")

            assert result == sample_feedback
            mock_critique_process.assert_called_once_with(
                query=sample_query,
                context={"report": sample_report}
            )
    
    @pytest.mark.asyncio
    async def test_revise_report(self, coordinator, sample_query, sample_report, sample_feedback):
        """Test report revision."""
        mock_db_manager = MagicMock()
        mock_db_manager.log_agent_message = AsyncMock()

        with patch.object(coordinator, 'db_manager', mock_db_manager), \
             patch.object(coordinator.reviser, 'process') as mock_revise_process:

            revised_report = sample_report
            revised_report.title = "Revised Report"
            mock_revise_process.return_value = revised_report

            result = await coordinator._revise_report(sample_query, sample_report, sample_feedback, "task123")

            assert result == revised_report
            mock_revise_process.assert_called_once_with(
                query=sample_query,
                context={"report": sample_report, "feedback": sample_feedback}
            )
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, coordinator):
        """Test getting task status."""
        mock_task_data = {
            "id": "task123",
            "status": "completed",
            "query": {"topic": "AI", "subtopics": [], "depth_level": 3, "requirements": None},
            "created_at": "2023-01-01T00:00:00"
        }

        mock_db_manager = MagicMock()
        mock_db_manager.get_task = AsyncMock(return_value=MagicMock(success=True, data=mock_task_data))

        with patch.object(coordinator, 'db_manager', mock_db_manager):
            result = await coordinator.get_task_status("task123")

            assert result is not None
            assert result.id == "task123"
            assert result.status == ResearchStatus.COMPLETED
