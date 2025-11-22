# Quick Start Guide

## Setting Up for Real Testing

### 1. Get Your API Keys

#### Supabase (Required)
1. Go to https://supabase.com
2. Create a new project or use existing
3. Go to Project Settings → API
4. Copy:
   - `URL` → This is your `SUPABASE_URL`
   - `service_role` key (secret) → This is your `SUPABASE_SERVICE_ROLE_KEY`

⚠️ **Important**: Use the `service_role` key (not `anon` key) for backend operations to avoid 400/401 errors!

#### Groq (Required)
1. Go to https://console.groq.com
2. Create account and generate API key
3. Copy the key → This is your `GROQ_API_KEY`

#### Tavily (Optional - Better Search Results)
1. Go to https://tavily.com
2. Sign up and get API key
3. Copy the key → This is your `TAVILY_API_KEY`

### 2. Setup Database

1. Open your Supabase project dashboard
2. Go to SQL Editor
3. Copy the contents of `supabase_schema_fixed.sql`
4. Paste and run in SQL Editor
5. Verify tables are created in Table Editor

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

**Minimal .env for testing:**
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
GROQ_API_KEY=your-groq-api-key-here
DEBUG=True
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Test the Integration

```bash
# Run the integration test
python test_real_integration.py
```

This will:
- ✓ Test database connection
- ✓ Test research tools (web, Wikipedia, arXiv)
- ✓ Run a complete research task
- ✓ Verify data is saved to Supabase

### 6. Run the Application

```bash
# Start the API server
python main.py
```

The API will be available at `http://localhost:8000`

### 7. Make a Test Request

```bash
# Create a research task
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Artificial Intelligence in Healthcare",
    "subtopics": ["Diagnosis", "Treatment Planning"],
    "depth_level": 3,
    "requirements": "Focus on recent developments"
  }'

# You'll get back a task_id like: {"task_id": "abc-123-def"}

# Check status (replace {task_id} with actual ID)
curl http://localhost:8000/api/research/{task_id}/status

# Get the report when completed
curl http://localhost:8000/api/research/{task_id}/report
```

### 8. Verify Data in Supabase

1. Go to your Supabase dashboard
2. Click "Table Editor"
3. Check these tables:
   - `research_tasks` - Should show your research task
   - `research_reports` - Should have the generated report
   - `critique_feedback` - Should have critique entries
   - `agent_messages` - Should have all agent logs

## Common Issues

### "401 Unauthorized" or "400 Bad Request"
**Solution**: Make sure you're using `SUPABASE_SERVICE_ROLE_KEY`, not the anon key.

### "No search results found"
**Normal**: DuckDuckGo API has limited results. Consider getting a Tavily API key for better results.

### "Database client not initialized"
**Solution**: Make sure the application called `coordinator.initialize()` before starting research.

### Logs showing errors
**Solution**: Enable `DEBUG=True` in `.env` to see detailed logs. Check `DEBUGGING_GUIDE.md` for specific error messages.

## What to Expect

When you run a research task:

1. **Data Gathering** (1-2 minutes):
   - Searches web (DuckDuckGo or Tavily)
   - Retrieves Wikipedia articles
   - Searches arXiv papers
   - All logged in real-time

2. **Report Generation** (30-60 seconds):
   - LLM synthesizes research data
   - Creates structured report with real sources

3. **Critique & Revision** (1-2 minutes):
   - Critic evaluates quality
   - If score < 7.0, reviser improves it
   - Repeats until quality threshold met

4. **Database Logging**:
   - Every step logged to Supabase
   - Task status updated in real-time
   - All agent messages saved

Total time: 2-5 minutes depending on topic complexity

## Monitoring Progress

Watch the console logs:
```
INFO - Initializing Supabase client with URL: ...
INFO - Using service_role key
INFO - Supabase client initialized successfully
INFO - Starting research on: [topic]
INFO - Gathering research data for topic: [topic]
INFO - Searching web for queries: ...
INFO - Found 9 web results
INFO - Gathered 3 Wikipedia articles
INFO - Gathered 5 arXiv papers
INFO - Conducting initial research...
INFO - Initial research completed. Generated report with 4 sections.
INFO - Analyzing report quality and providing feedback...
INFO - Critique completed. Overall score: 7.5/10
INFO - Research completed successfully for: [topic]
```

## Next Steps

- See `README.md` for full documentation
- See `DEBUGGING_GUIDE.md` for troubleshooting
- Check API documentation at `http://localhost:8000/docs` when running

## Tips for Better Results

1. **Use specific topics**: "Machine Learning in Medical Diagnosis" vs "AI"
2. **Include subtopics**: Helps guide the research focus
3. **Set appropriate depth**: 1-5 scale, 3 is good for testing
4. **Use Tavily API**: Much better search results than DuckDuckGo
5. **Monitor Supabase**: Watch tables fill in real-time

Happy researching! 🚀
