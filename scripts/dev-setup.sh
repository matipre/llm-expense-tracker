#!/bin/bash

# Darwin Challenge - Development Setup Script

echo "🚀 Setting up Darwin Challenge with Supabase CLI..."

# Install dependencies (including Supabase CLI)
echo "📦 Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Initialize and start Supabase
echo "🚀 Starting Supabase local development environment..."
if [ ! -f "supabase/config.toml" ]; then
    echo "🔧 Initializing Supabase project..."
    npx supabase init
    if [ $? -ne 0 ]; then
        echo "❌ Failed to initialize Supabase project"
        exit 1
    fi
fi

echo "📦 Starting all Supabase services..."
npx supabase start
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Supabase services"
    echo "💡 Try running 'npx supabase stop' and then 'npx supabase start' manually"
    exit 1
fi

echo "⏳ Waiting for Supabase services to be ready..."
sleep 5

echo "📋 Getting Supabase connection details..."
SUPABASE_STATUS=$(npx supabase status)
echo "$SUPABASE_STATUS"
echo ""
echo "💡 Copy the DB URL above and update your apps/bot/knexfile.js if needed"
echo ""

# Install Node.js dependencies for database migrations (managed by bot service)
echo "📦 Installing Node.js dependencies for database management..."
cd apps/bot
if [ ! -d "node_modules" ]; then
    npm install
fi

# Run database migrations (owned by bot service)
echo "🗄️  Running database migrations..."
npm run migrate
if [ $? -ne 0 ]; then
    echo "❌ Database migrations failed"
    echo "💡 Make sure the DATABASE_URL in apps/bot/.env matches the DB URL shown above"
    echo "💡 Or update apps/bot/knexfile.js with the correct connection details"
    cd ../..
    exit 1
fi

echo "🌱 Running database seeds..."
npm run seed
if [ $? -ne 0 ]; then
    echo "❌ Database seeding failed"
    echo "💡 Migrations succeeded but seeding failed. This might be OK if seeds already exist."
fi
cd ../..

echo "✅ Database setup complete!"

# Install dependencies if not already installed
echo "📦 Installing dependencies..."
cd apps/connector
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ../bot
if [ ! -d "node_modules" ] && [ ! -f "requirements_installed.flag" ]; then
    python3 -m pip install -r requirements.txt
    touch requirements_installed.flag
fi
cd ../..

echo "✅ Development environment setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Copy environment templates:"
echo "      cp apps/connector/env.template apps/connector/.env"
echo "      cp apps/bot/env.template apps/bot/.env"
echo ""
echo "   2. Update your .env files with the connection details shown above:"
echo "      - SUPABASE_URL (API URL)"
echo "      - SUPABASE_SERVICE_KEY (service_role key)"  
echo "      - DATABASE_URL (DB URL) for apps/bot/.env"
echo ""
echo "   3. Add your API keys:"
echo "      - TELEGRAM_BOT_TOKEN in apps/connector/.env"
echo "      - OPENAI_API_KEY in apps/bot/.env"
echo ""
echo "   4. Start the services:"
echo "      npm run dev"
echo ""
echo "🎛️  Supabase Dashboard: http://localhost:54323"
echo "📧 Email Testing: http://localhost:54324"
echo ""
