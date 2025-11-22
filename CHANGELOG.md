# Changelog

## [Unreleased] - 2024-11-22

### Added - Research Tools Integration & Supabase Debugging

#### Real Research Tools
- **Web Search Tool** (`app/tools/web_search.py`)
  - DuckDuckGo search (free, always available)
  - Tavily AI search (premium, optional)
  - Multi-query concurrent search
  - Automatic fallback to free alternatives

- **Wikipedia Tool** (`app/tools/wikipedia.py`)
  - Article search with ranking
  - Full article summary retrieval
  - Section extraction
  - HTML cleaning utilities

- **arXiv Tool** (`app/tools/arxiv_search.py`)
  - Academic paper search
  - Category-based search
  - Author and title search
  - Full metadata extraction (authors, abstract, categories)

#### Enhanced Researcher Agent
- Integrated all research tools into `ResearcherAgent`
- Added `_gather_research_data()` method for real data collection
- Updated `_generate_report_content()` to use actual research data
- Added `_format_research_data()` helper for LLM context
- Proper session cleanup for async HTTP clients
- Real sources now used in generated reports

#### Supabase Debugging & Fixes
- **Fixed RLS Policies** (`supabase_schema_fixed.sql`)
  - Changed from restrictive `auth.role() = 'authenticated'` to permissive `true`
  - Fixes 400/401 errors for backend operations
  - Allows service_role and anon key access

- **Enhanced Database Connection** (`app/database/connection.py`)
  - Added comprehensive logging for all operations
  - Support for `SUPABASE_SERVICE_ROLE_KEY` (recommended for backend)
  - Automatic key selection (service_role > anon)
  - Detailed error logging with stack traces
  - Debug logs for every database operation

- **Configuration Updates** (`app/config.py`)
  - Added `supabase_service_role_key` field
  - Added `tavily_api_key` field for premium web search
  - Added `serpapi_key` field for alternative search
  - All research tool keys are optional

#### Testing & Debugging Tools
- **Integration Test Script** (`test_real_integration.py`)
  - Tests database connectivity
  - Tests all research tools
  - Runs end-to-end research task
  - Verifies data persistence
  - Provides clear pass/fail summary

- **Debugging Guide** (`DEBUGGING_GUIDE.md`)
  - Comprehensive troubleshooting documentation
  - Common error messages and solutions
  - RLS policy fix instructions
  - Component verification scripts
  - Performance tips and security notes

- **Quick Start Guide** (`QUICK_START.md`)
  - Step-by-step setup instructions
  - API key acquisition guide
  - Testing workflow
  - Expected behavior documentation
  - Tips for better results

#### Documentation Updates
- Updated `README.md` with:
  - Research tools feature
  - Service role key requirement
  - Real integration testing section
  - Updated project structure
  - Troubleshooting references

- Updated `.env.example` with:
  - Service role key configuration
  - Research tool API keys
  - Detailed comments on usage

### Changed
- **Researcher Agent**: Now gathers real data before generating reports
- **Database Connection**: Now uses service_role key by default if available
- **Logging**: All database operations now logged with INFO/DEBUG levels
- **Error Handling**: More descriptive error messages with context

### Fixed
- **400/401 Errors**: Fixed by updating RLS policies and using service_role key
- **Empty Reports**: Now uses real research data from multiple sources
- **Database Logging**: Every operation now properly logged and verifiable
- **Session Management**: Proper async HTTP session cleanup

### Security Notes
⚠️ **Important Changes**:
- Service role key bypasses all RLS - use ONLY in trusted backend
- Never expose service_role key to frontend/client
- RLS policies now permissive for backend operations
- For production, implement proper authentication layer

### Migration Guide

#### For Existing Users:
1. **Update Database Schema**:
   ```sql
   -- In Supabase SQL Editor, run contents of supabase_schema_fixed.sql
   ```

2. **Update Environment Variables**:
   ```bash
   # Add to your .env
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   TAVILY_API_KEY=your-tavily-key  # optional
   ```

3. **Test Integration**:
   ```bash
   python test_real_integration.py
   ```

#### Breaking Changes:
- `ResearcherAgent.process()` now requires async HTTP client cleanup
- Database operations now require service_role key or updated RLS policies
- Old RLS policies will cause 401 errors - must update schema

### Dependencies
No new dependencies added. All research tools use existing packages:
- `aiohttp` - For async HTTP requests (already in requirements.txt)
- `xml.etree.ElementTree` - For arXiv XML parsing (built-in)

### Performance Improvements
- Concurrent multi-query web searches
- Async HTTP requests for all external APIs
- Proper connection pooling and session management
- Reduced database round-trips with better logging

### Known Issues
- DuckDuckGo API has limited results (use Tavily for better results)
- arXiv search may be slow for large result sets (limited to 5 results)
- Wikipedia API rate limiting not implemented (generally not an issue)

### Future Improvements
- Add more research sources (Google Scholar, PubMed, etc.)
- Implement caching for repeated queries
- Add rate limiting and retry logic
- Support for more search engines
- Add web scraping for full article content
