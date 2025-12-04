#!/bin/bash
# Start script for Telegram Video Bot

set -e

echo "🚀 Starting Telegram Video Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure it"
    exit 1
fi

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    exec python3 run.py
else
    # Check if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        echo "🐳 Starting with Docker Compose..."
        docker-compose up -d
        echo "✅ Bot started! View logs with: docker-compose logs -f"
    else
        echo "⚙️  Starting locally with Python..."
        # Check if virtual environment exists
        if [ ! -d "venv" ] && [ ! -d "env" ]; then
            echo "📦 Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        if [ -d "venv" ]; then
            source venv/bin/activate
        elif [ -d "env" ]; then
            source env/bin/activate
        fi
        
        # Install dependencies
        echo "📦 Installing dependencies..."
        pip install -q -r requirements.txt
        
        # Run the bot
        echo "▶️  Running bot..."
        python3 run.py
    fi
fi
