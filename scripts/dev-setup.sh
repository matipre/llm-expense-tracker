#!/bin/bash

# Expensio - Development Setup Script
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

echo "📦 Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "🐍 Installing Python dependencies..."
cd apps/bot
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
cd ../..

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