#!/bin/bash
# Setup PostgreSQL database for BytePort using same instance as Zen

set -e

echo "Setting up BytePort database in Zen PostgreSQL instance..."

# Database credentials
DB_USER="zen"
DB_PASSWORD="zen"
DB_NAME="zen_mcp"
DB_HOST="localhost"
DB_PORT="5432"

# Test connection
echo "Testing PostgreSQL connection..."
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on $DB_HOST:$DB_PORT"
    echo "Please start PostgreSQL first"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Create database if it doesn't exist (using psql)
echo "Ensuring database exists..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME"

echo "✅ Database $DB_NAME is ready"

# Export DATABASE_URL for the application
export DATABASE_URL="host=$DB_HOST user=$DB_USER password=$DB_PASSWORD dbname=$DB_NAME port=$DB_PORT sslmode=disable"

echo "✅ Database setup complete!"
echo ""
echo "Connection string: $DATABASE_URL"
echo ""
echo "To use this database, either:"
echo "1. Export DATABASE_URL before running the app:"
echo "   export DATABASE_URL=\"$DATABASE_URL\""
echo "   go run *.go"
echo ""
echo "2. Or the app will use the default connection to zen_mcp"
