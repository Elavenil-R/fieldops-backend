CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    location TEXT NOT NULL,
    issue TEXT NOT NULL,
    priority TEXT CHECK (priority IN ('High', 'Medium', 'Low')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'inprogress', 'completed', 'cancelled')),
    is_deleted BOOLEAN DEFAULT FALSE,
    is_saved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Migration for existing table
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS is_saved BOOLEAN DEFAULT FALSE;

-- Ensure is_deleted exists if not present
ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

-- Update status constraint if necessary
-- Note: PostgreSQL doesn't allow direct update of constraints easily without dropping and recreating, 
-- but this is a reference script.