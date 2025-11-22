# Debugging Guide for Supabase Integration

## Common Issues and Solutions

### 1. Supabase 400/401 Errors

#### Problem
Getting 400 (Bad Request) or 401 (Unauthorized) errors when saving data to Supabase.

#### Root Cause
The original schema had Row Level Security (RLS) policies that required `auth.role() = 'authenticated'`, but the application uses the anon key without authentication.

#### Solution
There are two ways to fix this:

**Option A: Use Service Role Key (Recommended for Backend)**
1. Get your service_role key from Supabase dashboard:
   - Go to Project Settings → API
   - Copy the `service_role` key (secret, never expose to frontend)

2. Add to your `.env` file:
   ```bash
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

3. The application will automatically use the service role key if available, which bypasses RLS.

**Option B: Update RLS Policies**
Apply the fixed schema that allows anon access:
```bash
# Use the fixed schema
psql postgresql://[your-connection-string] -f supabase_schema_fixed.sql
```

Or manually update policies in Supabase SQL Editor:
```sql
-- Drop old restrictive policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON research_tasks;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON research_reports;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON critique_feedback;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON agent_messages;

-- Create new permissive policies for backend service
CREATE POLICY "Enable all operations for service role and anon" ON research_tasks
    FOR ALL 
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable all operations for service role and anon" ON research_reports
    FOR ALL 
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable all operations for service role and anon" ON critique_feedback
    FOR ALL 
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable all operations for service role and anon" ON agent_messages
    FOR ALL 
    USING (true)
    WITH CHECK (true);
```

### 2. Debugging Database Operations

The application now includes comprehensive logging. Enable debug mode to see detailed logs:

```bash
# In .env file
DEBUG=True
```

You'll see logs like:
- `Initializing Supabase client with URL: ...`
- `Creating task with data: ...`
- `Task created successfully with ID: ...`
- `Saving feedback for task_id: ...`
- `Database error while saving feedback: ...`

### 3. Verifying Data is Being Saved

Check your Supabase dashboard:
1. Go to Table Editor
2. Check these tables:
   - `research_tasks` - Should have entries for each research request
   - `research_reports` - Should have reports linked to tasks
   - `critique_feedback` - Should have critique entries
   - `agent_messages` - Should have all agent logs

If tables are empty, check:
- Application logs for errors
- RLS policies are correct
- API keys are valid

### 4. Testing with Real LLM and Supabase

1. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your real credentials
   ```

2. **Required credentials**:
   - `SUPABASE_URL` - Your project URL
   - `SUPABASE_SERVICE_ROLE_KEY` - Service role key (recommended)
   - `GROQ_API_KEY` - Your Groq API key

3. **Optional (for better research)**:
   - `TAVILY_API_KEY` - For premium web search
   - `SERPAPI_KEY` - Alternative search API

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/api/research \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Quantum Computing Applications",
       "subtopics": ["Quantum Algorithms", "Quantum Hardware"],
       "depth_level": 3,
       "requirements": "Focus on practical applications"
     }'
   ```

6. **Check task status**:
   ```bash
   curl http://localhost:8000/api/research/{task_id}
   ```

### 5. Research Tools Integration

The application now integrates real research tools:

#### Web Search
- **DuckDuckGo**: Free, always available (limited results)
- **Tavily**: Premium, better quality (requires API key)

#### Wikipedia
- Full text search and article retrieval
- Automatic summarization
- No API key needed

#### arXiv
- Academic paper search
- Full metadata and abstracts
- No API key needed

To verify research tools are working, check logs for:
```
INFO - Gathering research data for topic: ...
INFO - Searching web for queries: ...
INFO - Found X web results
INFO - Searching Wikipedia for: ...
INFO - Gathered X Wikipedia articles
INFO - Searching arXiv for: ...
INFO - Gathered X arXiv papers
```

### 6. Monitoring Research Progress

The application logs every step:
```
INFO - Starting research on: [topic]
INFO - Conducting initial research...
INFO - Gathering research data for topic: [topic]
INFO - Initial research completed. Generated report with X sections.
INFO - Analyzing report quality and providing feedback...
INFO - Critique completed. Overall score: X.X/10
INFO - Research completed successfully
```

### 7. Common Error Messages

**"Database client not initialized"**
- Solution: Ensure `coordinator.initialize()` is called before research

**"Failed to initialize Supabase client"**
- Check SUPABASE_URL is correct
- Check SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY is valid
- Check network connectivity

**"Database error while creating task"**
- Check RLS policies (use service_role key or update policies)
- Check table exists in database
- Check column types match model

**"No research results found"**
- Normal for some queries with DuckDuckGo
- Consider using Tavily API for better results
- Check network connectivity

### 8. Verifying Each Component

#### Test Database Connection
```python
from app.database.connection import db_manager
import asyncio

async def test_db():
    result = await db_manager.initialize()
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")

asyncio.run(test_db())
```

#### Test Research Tools
```python
from app.tools.web_search import WebSearchTool
from app.tools.wikipedia import WikipediaTool
from app.tools.arxiv_search import ArxivTool
import asyncio

async def test_tools():
    # Test web search
    web = WebSearchTool()
    results = await web.search("artificial intelligence")
    print(f"Web results: {len(results)}")
    await web.close()
    
    # Test Wikipedia
    wiki = WikipediaTool()
    results = await wiki.search("machine learning")
    print(f"Wiki results: {len(results)}")
    await wiki.close()
    
    # Test arXiv
    arxiv = ArxivTool()
    results = await arxiv.search("neural networks")
    print(f"arXiv results: {len(results)}")
    await arxiv.close()

asyncio.run(test_tools())
```

## Performance Tips

1. **Use service_role key** for backend operations (bypasses RLS overhead)
2. **Enable DEBUG=False** in production for better performance
3. **Use Tavily API** for faster, more reliable web search
4. **Adjust MAX_RETRIES** based on quality requirements
5. **Monitor database indexes** for query performance

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit `.env` file to git
- Never expose service_role key to frontend/client
- Service_role key bypasses all RLS - use only in trusted backend
- For production, implement proper authentication and user-specific RLS policies
