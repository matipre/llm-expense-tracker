#!/bin/bash

# Expensio - Development Setup Script

echo "🚀 Setting up Expensio database service with centralized .env configuration..."

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
echo "🐳 Starting Docker services: expensio..."
docker-compose --project-name expensio up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start expensio services"
    exit 1
fi

# Wait for expensio service to be healthy
echo "⏳ Waiting for expensio services to be ready..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose --project-name expensio ps postgres | grep -q "healthy" && docker-compose --project-name expensio ps rabbitmq | grep -q "healthy"; then
        echo "✅ Expensio services are healthy"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "⚠️ Expensio services may not be fully ready, but continuing..."
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

echo "🗄️  Services started:"
echo "  PostgreSQL: localhost:5432, DB: expensio, User: expensio_user"
echo "  RabbitMQ: localhost:5672 (AMQP), localhost:15672 (Management UI)"