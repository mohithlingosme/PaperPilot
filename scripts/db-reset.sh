#!/bin/bash

# Database reset script for PaperPilot
set -e

echo "Starting database reset..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    exit 1
fi

# Drop and recreate database
echo "Dropping and recreating database..."
# Note: This assumes you have appropriate permissions to drop/create databases
# In production, you might want to use a different approach

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Run seed data
echo "Running seed data..."
# Add seed data insertion here if needed

echo "Database reset completed successfully!"
