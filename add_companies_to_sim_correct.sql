-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  password_hash VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Add company_id to users table (if it exists)
ALTER TABLE users ADD COLUMN IF NOT EXISTS company_id VARCHAR REFERENCES companies(id);

-- Insert 5 companies (with hashed passwords in production)
INSERT INTO companies (id, name, password_hash) VALUES
('prodco1', 'Documentary House', 'Demo2024!'),
('prodco2', 'TrueCrime Productions', 'Test2024!'),
('prodco3', 'Netflix Originals', 'Pilot2024!'),
('prodco4', 'Indie Films Co', 'Story2024!'),
('prodco5', 'Test Company', 'Develop2024!')
ON CONFLICT (id) DO NOTHING;

-- Create or update users for each company
INSERT INTO users (id, email, company_id) VALUES
('c50f98ec-1234-5678-9abc-def012345678', 'prodco1@sim.com', 'prodco1'),
('a12f98ec-5678-1234-9abc-abc123456789', 'prodco2@sim.com', 'prodco2'),
('b34f98ec-9012-3456-7890-def098765432', 'prodco3@sim.com', 'prodco3'),
('d56f98ec-3456-7890-1234-ghi567890123', 'prodco4@sim.com', 'prodco4'),
('e78f98ec-6789-0123-4567-jkl890123456', 'prodco5@sim.com', 'prodco5')
ON CONFLICT (id) DO UPDATE SET company_id = EXCLUDED.company_id;
