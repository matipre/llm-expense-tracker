#!/bin/bash

# Development Setup Script for Supabase
# This script sets up the local development environment

set -e

echo "🚀 Setting up Supabase development environment..."

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    npm install -g supabase
fi

# Check if we're in the right directory
if [ ! -f "supabase/config.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Supabase CLI found. Setting up development environment..."

# Start Supabase services
echo "🚀 Starting Supabase services..."
supabase start

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Apply migrations
echo "📊 Applying database migrations..."
supabase db push

# Apply seed data
echo "🌱 Applying seed data..."
psql postgresql://postgres:postgres@localhost:54322/postgres -f supabase/seed.sql

echo "✅ Development environment setup completed!"
echo ""
echo "📊 Your Supabase instance is running at:"
echo "   - API: http://localhost:54321"
echo "   - Studio: http://localhost:54323"
echo "   - Database: localhost:54322"
echo ""
echo "🔑 Default credentials:"
echo "   - Email: supabase_admin@admin.com"
echo "   - Password: this-is-a-very-long-secret-that-is-at-least-32-characters-long"
echo ""
echo "📚 Useful commands:"
echo "   - Stop services: supabase stop"
echo "   - View logs: supabase logs"
echo "   - Create new migration: ./supabase/create-migration.sh <name>"
echo "   - Apply new migrations: supabase db push"
echo "   - Reset database: supabase db reset (⚠️  WARNING: This will delete all data!)"
