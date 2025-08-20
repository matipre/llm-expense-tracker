#!/bin/bash

# Supabase Migration Creation Script
# This script helps create new migrations using Supabase CLI

set -e

if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <migration_name>"
    echo "   Example: $0 add_new_feature"
    exit 1
fi

MIGRATION_NAME=$1
TIMESTAMP=$(date +%Y%m%d%H%M%S)
FILENAME="${TIMESTAMP}_${MIGRATION_NAME}.sql"

echo "🚀 Creating new Supabase migration: $FILENAME"

# Create the migration file
cat > "supabase/migrations/$FILENAME" << EOF
-- Migration: $MIGRATION_NAME
-- Created: $(date)
-- Description: Add your migration description here

-- Your SQL migration code goes here
-- Example:
-- CREATE TABLE example (
--     id SERIAL PRIMARY KEY,
--     name TEXT NOT NULL
-- );

-- Don't forget to add rollback logic if needed
EOF

echo "✅ Created migration file: migrations/$FILENAME"
echo ""
echo "📝 Next steps:"
echo "   1. Edit the migration file with your SQL"
echo "   2. Test locally: supabase db push"
echo "   3. Commit the migration file"
echo "   4. Deploy to production: supabase db push --linked"
