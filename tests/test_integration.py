"""Integration tests for the complete research system."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.orchestrator.coordinator import ResearchCoordinator
from app.models.research import ResearchQuery, ResearchStatus


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_complete_research_flow(self):
        """Test the complete research flow from start to finish."""
        coordinator = ResearchCoordinator()
        query = ResearchQuery(
            topic="Quantum Computing",
            subtopics=["Quantum Algorithms", "Quantum Hardware"],
            depth_level=3,
            requirements="Focus on recent developments"
        )
        
        # Mock the entire system
        with patch('app.database.connection.db_manager') as mock_db_manager, \
             patch.object(coordinator, 'initialize') as mock_init:
            
            # Setup mocks
            mock_init.return_value = True
            mock_db_manager.create_task = AsyncMock(return_value=MagicMock(success=True, data={"id": "integration_test_123"}))
            
            # Mock LLM responses for researcher
            mock_research_plan = {
                "key_areas": ["Quantum basics", "Current applications"],
                "source_types": ["academic", "technical"],
                "report_structure": ["intro", "analysis", "conclusion"],
                "research_questions": ["What is quantum computing?"],
                "challenges": ["Technical complexity"]
            }
            
            mock_research_report = {
                "abstract": "Quantum computing represents a paradigm shift in computational technology...",
                "sections": [
                    {
                        "title": "Introduction to Quantum Computing",
                        "content": "Quantum computing harnesses quantum mechanical phenomena...",
                        "sources": [
                            {
                                "title": "Quantum Computing Fundamentals",
                                "url": "https://example.com/quantum-fundamentals",
                                "content": "Comprehensive overview of quantum computing principles",
                                "credibility_score": 0.95
                            }
                        ],
                        "confidence_score": 0.85
                    },
                    {
                        "title": "Quantum Algorithms",
                        "content": "Several quantum algorithms demonstrate computational advantages...",
                        "sources": [
                            {
                                "title": "Shor's Algorithm Explained",
                                "url": "https://example.com/shors-algorithm",
                                "content": "Detailed explanation of Shor's factoring algorithm",
                                "credibility_score": 0.90
                            }
                        ],
                        "confidence_score": 0.80
                    }
                ],
                "conclusion": "Quantum computing holds tremendous potential for solving complex problems...",
                "sources": [
                    {
                        "title": "Quantum Computing Fundamentals",
                        "url": "https://example.com/quantum-fundamentals",
                        "content": "Comprehensive overview of quantum computing principles",
                        "credibility_score": 0.95
                    },
                    {
                        "title": "Shor's Algorithm Explained",
                        "url": "https://example.com/shors-algorithm",
                        "content": "Detailed explanation of Shor's factoring algorithm",
                        "credibility_score": 0.90
                    }
                ]
            }
            
            # Mock LLM responses for critic (high quality to avoid revisions)
            mock_critique_feedback = {
                "overall_score": 8.5,
                "strengths": [
                    "Comprehensive coverage of quantum computing fundamentals",
                    "Well-structured sections with logical flow",
                    "High-quality, credible sources"
                ],
                "weaknesses": [
                    "Could include more recent developments in quantum hardware"
                ],
                "suggestions": [
                    "Add section on current quantum hardware implementations",
                    "Include more specific examples of quantum algorithms"
                ],
                "specific_corrections": {},
                "priority_issues": []
            }
            
            # Setup mock responses
            with patch.object(coordinator.researcher, 'generate_structured_llm_response') as mock_researcher_llm, \
                 patch.object(coordinator.critic, 'generate_structured_llm_response') as mock_critic_llm:
                
                mock_researcher_llm.side_effect = [mock_research_plan, mock_research_report]
                mock_critic_llm.return_value = mock_critique_feedback
                
                # Execute the research
                task = await coordinator.conduct_research(query)
                
                # Verify the complete flow
                assert task is not None
                assert task.query == query
                assert task.status == ResearchStatus.COMPLETED
                assert task.current_report is not None
                assert task.current_report.title == "Research Report: Quantum Computing"
                assert len(task.current_report.sections) == 2
                assert len(task.current_report.sources) == 2
                
                # Verify database operations were called
                mock_create_task.assert_called_once()
                assert mock_save_report.call_count >= 1  # At least initial report saved
                mock_save_feedback.assert_called_once()
                assert mock_log_message.call_count >= 3  # Multiple agent messages
                assert mock_update_task.call_count >= 1  # Status updates
    
    @pytest.mark.asyncio
    async def test_research_with_revisions(self):
        """Test research flow that requires multiple revisions."""
        coordinator = ResearchCoordinator()
        query = ResearchQuery(
            topic="Climate Change",
            depth_level=4
        )
        
        with patch('app.database.connection.db_manager') as mock_db_manager, \
             patch.object(coordinator, 'initialize') as mock_init:
            
            mock_init.return_value = True
            mock_db_manager.create_task = AsyncMock(return_value=MagicMock(success=True, data={"id": "revision_test_123"}))
            
            # Mock initial research (low quality)
            mock_initial_report = {
                "abstract": "Brief abstract",
                "sections": [
                    {
                        "title": "Basic Info",
                        "content": "Basic content about climate change",
                        "sources": [
                            {
                                "title": "Basic Source",
                                "url": "https://example.com/basic",
                                "content": "Basic information",
                                "credibility_score": 0.6
                            }
                        ],
                        "confidence_score": 0.5
                    }
                ],
                "conclusion": "Simple conclusion",
                "sources": [
                    {
                        "title": "Basic Source",
                        "url": "https://example.com/basic",
                        "content": "Basic information",
                        "credibility_score": 0.6
                    }
                ]
            }
            
            # Mock critique feedback (low score, requires revision)
            mock_critique_low = {
                "overall_score": 5.5,
                "strengths": ["Covers basic topic"],
                "weaknesses": ["Lacks depth", "Poor sources"],
                "suggestions": ["Add scientific data", "Improve sources"],
                "specific_corrections": {
                    "abstract": "Make more comprehensive",
                    "conclusion": "Add specific recommendations"
                },
                "priority_issues": ["Add peer-reviewed sources", "Include recent data"]
            }
            
            # Mock revised report (better quality)
            mock_revised_report = {
                "abstract": "Comprehensive abstract about climate change with recent data",
                "sections": [
                    {
                        "title": "Climate Change: Scientific Evidence",
                        "content": "Detailed scientific evidence with peer-reviewed sources",
                        "sources": [
                            {
                                "title": "IPCC Climate Report 2023",
                                "url": "https://ipcc.ch/report",
                                "content": "Latest IPCC assessment report",
                                "credibility_score": 0.95
                            }
                        ],
                        "confidence_score": 0.9
                    }
                ],
                "conclusion": "Detailed conclusion with specific recommendations",
                "sources": [
                    {
                        "title": "IPCC Climate Report 2023",
                        "url": "https://ipcc.ch/report",
                        "content": "Latest IPCC assessment report",
                        "credibility_score": 0.95
                    }
                ]
            }
            
            # Mock final critique (high quality)
            mock_critique_high = {
                "overall_score": 8.5,
                "strengths": ["Comprehensive coverage", "Excellent sources"],
                "weaknesses": [],
                "suggestions": [],
                "specific_corrections": {},
                "priority_issues": []
            }
            
            # Setup mock responses
            with patch.object(coordinator.researcher, 'generate_structured_llm_response') as mock_researcher_llm, \
                 patch.object(coordinator.critic, 'generate_structured_llm_response') as mock_critic_llm, \
                 patch.object(coordinator.reviser, 'generate_structured_llm_response') as mock_reviser_llm:
                
                # Researcher initial response
                mock_researcher_llm.return_value = mock_initial_report
                
                # Critic responses (low then high)
                mock_critic_llm.side_effect = [mock_critique_low, mock_critique_high]
                
                # Reviser response
                mock_reviser_llm.return_value = mock_revised_report
                
                # Execute the research
                task = await coordinator.conduct_research(query)
                
                # Verify the flow with revisions
                assert task is not None
                assert task.status == ResearchStatus.COMPLETED
                assert task.current_report is not None
                
                # Verify multiple saves (initial + revised)
                assert mock_save_report.call_count >= 2
                
                # Verify multiple critiques
                assert mock_save_feedback.call_count >= 2
                
                # Verify revision process was triggered
                mock_reviser_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in the research flow."""
        coordinator = ResearchCoordinator()
        query = ResearchQuery(topic="Test Topic")
        
        with patch.object(coordinator, 'initialize') as mock_init:
            mock_init.return_value = False  # Initialization fails
            
            # Should handle initialization failure gracefully
            with pytest.raises(Exception):
                await coordinator.conduct_research(query)
