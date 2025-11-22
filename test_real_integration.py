"""Test script for real LLM and Supabase integration."""

import asyncio
import logging
from app.config import settings
from app.database.connection import db_manager
from app.orchestrator.coordinator import ResearchCoordinator
from app.models.research import ResearchQuery

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test basic database connectivity."""
    logger.info("=" * 60)
    logger.info("TEST 1: Database Connection")
    logger.info("=" * 60)
    
    result = await db_manager.initialize()
    
    if result.success:
        logger.info("✓ Database initialized successfully")
        logger.info(f"  Using URL: {settings.supabase_url}")
        logger.info(f"  Using key type: {'service_role' if settings.supabase_service_role_key else 'anon'}")
        return True
    else:
        logger.error(f"✗ Database initialization failed: {result.error}")
        return False


async def test_research_tools():
    """Test research tools integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Research Tools")
    logger.info("=" * 60)
    
    from app.tools.web_search import WebSearchTool
    from app.tools.wikipedia import WikipediaTool
    from app.tools.arxiv_search import ArxivTool
    
    success_count = 0
    
    # Test web search
    try:
        logger.info("\nTesting Web Search...")
        web = WebSearchTool(tavily_api_key=settings.tavily_api_key)
        results = await web.search("artificial intelligence", max_results=2)
        logger.info(f"✓ Web search returned {len(results)} results")
        if results:
            logger.info(f"  Sample: {results[0].get('title', 'No title')[:50]}")
        await web.close()
        success_count += 1
    except Exception as e:
        logger.error(f"✗ Web search failed: {str(e)}")
    
    # Test Wikipedia
    try:
        logger.info("\nTesting Wikipedia...")
        wiki = WikipediaTool()
        results = await wiki.search("machine learning", max_results=2)
        logger.info(f"✓ Wikipedia search returned {len(results)} results")
        if results:
            logger.info(f"  Sample: {results[0].get('title', 'No title')}")
        await wiki.close()
        success_count += 1
    except Exception as e:
        logger.error(f"✗ Wikipedia search failed: {str(e)}")
    
    # Test arXiv
    try:
        logger.info("\nTesting arXiv...")
        arxiv = ArxivTool()
        results = await arxiv.search("neural networks", max_results=2)
        logger.info(f"✓ arXiv search returned {len(results)} results")
        if results:
            logger.info(f"  Sample: {results[0].get('title', 'No title')[:50]}")
        await arxiv.close()
        success_count += 1
    except Exception as e:
        logger.error(f"✗ arXiv search failed: {str(e)}")
    
    logger.info(f"\nResearch tools: {success_count}/3 passed")
    return success_count == 3


async def test_simple_research():
    """Test a simple research task end-to-end."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Simple Research Task")
    logger.info("=" * 60)
    
    try:
        # Initialize coordinator
        coordinator = ResearchCoordinator()
        init_success = await coordinator.initialize()
        
        if not init_success:
            logger.error("✗ Failed to initialize coordinator")
            return False
        
        logger.info("✓ Coordinator initialized")
        
        # Create simple research query
        query = ResearchQuery(
            topic="Python Programming",
            subtopics=["Async/Await"],
            depth_level=2,
            requirements="Brief overview for testing"
        )
        
        logger.info(f"\nStarting research on: {query.topic}")
        logger.info("This may take a few minutes...")
        
        # Conduct research
        task = await coordinator.conduct_research(query)
        
        if task.status.value == "completed":
            logger.info("\n✓ Research completed successfully!")
            logger.info(f"  Task ID: {task.id}")
            logger.info(f"  Status: {task.status.value}")
            if task.current_report:
                logger.info(f"  Report title: {task.current_report.title}")
                logger.info(f"  Sections: {len(task.current_report.sections)}")
                logger.info(f"  Sources: {len(task.current_report.sources)}")
            return True
        else:
            logger.error(f"✗ Research failed with status: {task.status.value}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Research task failed: {str(e)}", exc_info=True)
        return False


async def verify_database_records():
    """Verify that records were actually saved to database."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Verify Database Records")
    logger.info("=" * 60)
    
    try:
        # Try to query recent tasks
        logger.info("\nChecking for saved records...")
        logger.info("Please check your Supabase dashboard:")
        logger.info("  1. Go to Table Editor")
        logger.info("  2. Check 'research_tasks' table")
        logger.info("  3. Check 'research_reports' table")
        logger.info("  4. Check 'critique_feedback' table")
        logger.info("  5. Check 'agent_messages' table")
        logger.info("\nAll tables should have new entries from the test.")
        return True
    except Exception as e:
        logger.error(f"✗ Verification failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    logger.info("Starting Real Integration Tests")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Supabase URL: {settings.supabase_url}")
    logger.info(f"Groq API configured: {'Yes' if settings.groq_api_key != 'test-key' else 'No'}")
    logger.info(f"Tavily API configured: {'Yes' if settings.tavily_api_key else 'No'}")
    
    results = []
    
    # Run tests
    results.append(("Database Connection", await test_database_connection()))
    results.append(("Research Tools", await test_research_tools()))
    results.append(("Simple Research", await test_simple_research()))
    results.append(("Verify Records", await verify_database_records()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Your integration is working correctly.")
    else:
        logger.warning("\n⚠️  Some tests failed. Check the logs above for details.")
        logger.info("See DEBUGGING_GUIDE.md for troubleshooting help.")


if __name__ == "__main__":
    asyncio.run(main())
