# Self-Correcting Multi-Agent Research App

A sophisticated research application that uses multiple AI agents to conduct, critique, and revise research reports autonomously.

## Features

- **Multi-Agent System**: Researcher, Critic, and Reviser agents work together
- **Self-Correction**: Automatic quality assessment and iterative improvements
- **Async Architecture**: Fully asynchronous implementation for optimal performance
- **Database Integration**: Supabase for persistent storage and real-time updates
- **Pydantic Models**: Type-safe data validation and serialization
- **LLM Integration**: Uses Qwen model via Groq API
- **REST API**: FastAPI-based web service
- **Comprehensive Testing**: Full test suite with unit, integration, and end-to-end tests

## Architecture

### Agents

1. **Researcher Agent**: Conducts initial research and generates comprehensive reports
2. **Critic Agent**: Evaluates report quality and provides detailed feedback
3. **Reviser Agent**: Improves reports based on critique feedback

### Self-Correction Loop

The system implements an iterative improvement process:

1. Researcher generates initial report
2. Critic evaluates quality (score 0-10)
3. If score < 7.0, Reviser improves the report
4. Process repeats until quality threshold is met or max retries reached

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up Supabase database:
   ```bash
   # Apply the schema in supabase_schema.sql to your Supabase project
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Groq API Configuration
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=qwen-2.5-72b

# Application Settings
DEBUG=True
MAX_RETRIES=3
RESEARCH_TIMEOUT=300
```

## Usage

### Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /research` - Create a new research task
- `GET /research/{task_id}/status` - Get task status
- `GET /research/{task_id}/report` - Get final research report
- `GET /research/{task_id}/messages` - Get agent communication logs
- `GET /health` - Health check

### Example Usage

```python
import httpx

# Create a research task
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/research",
        json={
            "topic": "Quantum Computing",
            "subtopics": ["Quantum Algorithms", "Quantum Hardware"],
            "depth_level": 3,
            "requirements": "Focus on recent developments"
        }
    )
    task = response.json()
    task_id = task["task_id"]
    
    # Check status
    response = await client.get(f"http://localhost:8000/research/{task_id}/status")
    status = response.json()
    print(f"Task status: {status['status']}")
    
    # Get final report (when completed)
    response = await client.get(f"http://localhost:8000/research/{task_id}/report")
    report = response.json()
    print(f"Report title: {report['title']}")
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## Project Structure

```
app/
├── __init__.py
├── config.py              # Application configuration
├── models/                 # Pydantic models
│   ├── __init__.py
│   └── research.py
├── database/               # Database operations
│   ├── __init__.py
│   └── connection.py
├── llm/                    # LLM integration
│   ├── __init__.py
│   └── client.py
├── agents/                 # AI agents
│   ├── __init__.py
│   ├── base.py
│   ├── researcher.py
│   ├── critic.py
│   └── reviser.py
├── orchestrator/           # Multi-agent coordination
│   ├── __init__.py
│   └── coordinator.py
└── api/                    # REST API
    ├── __init__.py
    └── routes.py

tests/                      # Test suite
├── __init__.py
├── conftest.py
├── test_models.py
├── test_agents.py
├── test_orchestrator.py
└── test_integration.py

main.py                     # Application entry point
requirements.txt            # Dependencies
supabase_schema.sql         # Database schema
.env.example               # Environment variables template
```

## Data Models

### ResearchQuery
- `topic`: Main research topic
- `subtopics`: List of subtopics to explore
- `depth_level`: Research depth (1-5)
- `requirements`: Specific research requirements

### ResearchReport
- `title`: Report title
- `abstract`: Executive summary
- `sections`: List of research sections
- `conclusion`: Key findings and implications
- `sources`: All referenced sources
- `metadata`: Additional information

### CritiqueFeedback
- `overall_score`: Quality rating (0-10)
- `strengths`: Identified strengths
- `weaknesses`: Areas for improvement
- `suggestions`: Specific recommendations
- `specific_corrections`: Detailed corrections needed
- `priority_issues`: High-priority issues to address

## Quality Assurance

The system ensures high-quality research through:

1. **Multiple Perspectives**: Different agents provide complementary expertise
2. **Iterative Improvement**: Self-correction loop refines the output
3. **Quality Thresholds**: Minimum quality scores before completion
4. **Source Validation**: Credibility scoring for all sources
5. **Structured Feedback**: Detailed, actionable critique

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.
