#!/bin/bash

# Expensio - Development Setup Script

echo "🚀 Setting up Expensio with centralized .env configuration..."

# Check if centralized .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Centralized .env file not found in project root!"
    echo "Please create a .env file based on env.example:"
    echo "cp env.example .env"
    echo "Then edit .env with your actual values"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start Docker Compose services
echo "🐳 Starting Docker services (PostgreSQL & RabbitMQ)..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker services"
    exit 1
fi

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose ps | grep -q "healthy"; then
        echo "✅ Docker services are healthy"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "⚠️ Services may not be fully ready, but continuing..."
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Install Python dependencies for bot service
echo "🐍 Installing Python dependencies..."
cd apps/bot
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
cd ../..

# dotenv-cli is already installed in the main package.json
echo "✅ dotenv-cli available from main package.json"

echo "✅ Development environment setup completed!"
echo ""
echo "📋 Available commands:"
echo ""
echo "🚀 Start all services with centralized .env:"
echo "  npm run dev"
echo ""
echo "🐰 RabbitMQ Management UI:"
echo "  http://localhost:15672 (user: expensio_user, pass: expensio_password)"
echo ""
echo "🗄️  PostgreSQL Database:"
echo "  Host: localhost:5432, DB: expensio, User: expensio_user"