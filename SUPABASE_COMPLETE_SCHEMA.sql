-- S!M Complete Supabase Schema
-- Last Updated: September 2024
-- IMPORTANT: Use CREATE TABLE IF NOT EXISTS when running in production

-- Core Tables (use IF NOT EXISTS in production)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    synthesis_generated BOOLEAN DEFAULT FALSE,
    user_id UUID,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Continue with IF NOT EXISTS for all tables...
