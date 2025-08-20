-- Create message_queue table
CREATE TABLE IF NOT EXISTS message_queue (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL, -- 'telegram_message' or 'bot_response'
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_message_queue_type_status ON message_queue(type, status);
CREATE INDEX IF NOT EXISTS idx_message_queue_timestamp ON message_queue(timestamp);
CREATE INDEX IF NOT EXISTS idx_message_queue_status ON message_queue(status);

-- Add RLS (Row Level Security) policies
ALTER TABLE message_queue ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations on message queue (internal system table)
CREATE POLICY "Allow all operations on message queue" ON message_queue
    FOR ALL USING (true);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_message_queue_updated_at 
    BEFORE UPDATE ON message_queue 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
