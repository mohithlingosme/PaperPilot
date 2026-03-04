#!/bin/bash

# Database migration script for PaperPilot
set -e

echo "Starting database migration..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    exit 1
fi

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

echo "Database migration completed successfully!"
