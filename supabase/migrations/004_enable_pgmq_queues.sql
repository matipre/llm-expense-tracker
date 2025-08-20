-- Enable pgmq extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pgmq;

-- Create queues for telegram message flow using pgmq schema
SELECT pgmq.create('telegram_received_messages');
SELECT pgmq.create('telegram_bot_responses');

-- Log the creation (this will appear in Supabase logs)
DO $$
BEGIN
    RAISE NOTICE '🚀 PGMQ extension and queues created successfully';
    RAISE NOTICE '📋 Created queues: telegram_received_messages, telegram_bot_responses';
END $$;
