-- Seed data for PaperPilot database
-- Run after initial schema creation

-- Insert default roles
INSERT INTO roles (name) VALUES
('owner'),
('admin'),
('editor'),
('viewer')
ON CONFLICT (name) DO NOTHING;

-- Note: Default workspace and user creation should be handled by application code
-- This file only contains static seed data that doesn't depend on runtime values
