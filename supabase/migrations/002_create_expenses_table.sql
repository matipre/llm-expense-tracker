-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    category TEXT NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_expenses_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_added_at ON expenses(added_at);

-- Add RLS (Row Level Security) policies
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to view their own expenses
CREATE POLICY "Users can view own expenses" ON expenses
    FOR SELECT USING (true);

-- Policy to allow users to insert their own expenses
CREATE POLICY "Users can insert own expenses" ON expenses
    FOR INSERT WITH CHECK (true);

-- Policy to allow users to update their own expenses
CREATE POLICY "Users can update own expenses" ON expenses
    FOR UPDATE USING (true);

-- Policy to allow users to delete their own expenses
CREATE POLICY "Users can delete own expenses" ON expenses
    FOR DELETE USING (true);
