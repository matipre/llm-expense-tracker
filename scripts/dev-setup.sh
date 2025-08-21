#!/bin/bash

# Darwin Challenge - Development Setup Script

echo "🚀 Setting up Darwin Challenge with centralized .env configuration..."

# Check if centralized .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Centralized .env file not found in project root!"
    echo "Please create a .env file based on env.example:"
    echo "cp env.example .env"
    echo "Then edit .env with your actual values"
    exit 1
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
echo "🤖 Start Bot Service with .env:"
echo "  cd apps/bot && npm run dev:with-env"
echo ""
echo "🔗 Start Connector Service with .env:"
echo "  cd apps/connector && npm run dev:with-env"
echo ""
echo "🏗️  Deploy to Railway with Terraform:"
echo "  npm run terraform:deploy"
echo ""
echo "📊 View Railway status:"
echo "  railway status"
echo ""
echo "📝 View logs:"
echo "  railway logs"
