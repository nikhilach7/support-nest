#!/bin/bash

# Support Ticket System - Startup Script

echo "🎫 Support Ticket System - Starting..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   Get your API key from: https://platform.openai.com/"
    echo ""
    read -p "Press Enter to continue after adding your API key..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

export DOCKER_BUILDKIT=0

echo "🐳 Starting Docker containers..."
echo ""

# Build and start containers
docker-compose up --build

# If user exits with Ctrl+C
echo ""
echo "👋 Shutting down..."
docker-compose down
