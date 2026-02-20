@echo off
REM Support Ticket System - Windows Startup Script

echo.
echo 🎫 Support Ticket System - Starting...
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  No .env file found. Creating from example...
    copy .env.example .env
    echo ✅ Created .env file
    echo.
    echo ⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY
    echo    Get your API key from: https://platform.openai.com/
    echo.
    pause
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Disable BuildKit to avoid Dockerfile read issues on Windows
set DOCKER_BUILDKIT=0
set COMPOSE_DOCKER_CLI_BUILD=0

echo 🐳 Starting Docker containers...
echo.

REM Build and start containers
docker-compose up --build

REM If user exits with Ctrl+C
echo.
echo 👋 Shutting down...
docker-compose down
