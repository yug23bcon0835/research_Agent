-- Supabase database schema for the multi-agent research application

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Research tasks table
CREATE TABLE IF NOT EXISTS research_tasks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    query JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    current_report JSONB,
    feedback_history JSONB DEFAULT '[]',
    agent_messages JSONB DEFAULT '[]',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Research reports table
CREATE TABLE IF NOT EXISTS research_reports (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    task_id UUID REFERENCES research_tasks(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    abstract TEXT,
    sections JSONB DEFAULT '[]',
    conclusion TEXT,
    sources JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Critique feedback table
CREATE TABLE IF NOT EXISTS critique_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    task_id UUID REFERENCES research_tasks(id) ON DELETE CASCADE,
    overall_score DECIMAL(3,1) NOT NULL CHECK (overall_score >= 0.0 AND overall_score <= 10.0),
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    suggestions JSONB DEFAULT '[]',
    specific_corrections JSONB DEFAULT '{}',
    priority_issues JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent messages table
CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    task_id UUID REFERENCES research_tasks(id) ON DELETE CASCADE,
    agent_type VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_research_tasks_status ON research_tasks(status);
CREATE INDEX IF NOT EXISTS idx_research_tasks_created_at ON research_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_research_reports_task_id ON research_reports(task_id);
CREATE INDEX IF NOT EXISTS idx_critique_feedback_task_id ON critique_feedback(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_task_id ON agent_messages(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_timestamp ON agent_messages(timestamp);

-- Row Level Security (RLS) policies
ALTER TABLE research_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE critique_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (adjust as needed for production)
CREATE POLICY "Allow all operations for authenticated users" ON research_tasks
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON research_reports
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON critique_feedback
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON agent_messages
    FOR ALL USING (auth.role() = 'authenticated');

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_research_tasks_updated_at
    BEFORE UPDATE ON research_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_reports_updated_at
    BEFORE UPDATE ON research_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing (optional)
INSERT INTO research_tasks (
    query,
    status,
    created_at
) VALUES (
    '{"topic": "Artificial Intelligence", "subtopics": ["Machine Learning"], "depth_level": 3}',
    'completed',
    NOW()
) ON CONFLICT DO NOTHING;
