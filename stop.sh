#!/bin/bash
# Stop script for Telegram Video Bot

set -e

echo "🛑 Stopping Telegram Video Bot..."

# Check if running with docker-compose
if command -v docker-compose &> /dev/null && [ -f docker-compose.yml ]; then
    if docker-compose ps | grep -q "telegram-bot"; then
        echo "🐳 Stopping Docker containers..."
        docker-compose down
        echo "✅ Bot stopped!"
    else
        echo "ℹ️  Bot is not running in Docker"
    fi
else
    echo "ℹ️  Docker Compose not found or not configured"
fi

# Kill any running Python processes for the bot
if pgrep -f "python.*run.py" > /dev/null; then
    echo "🔪 Killing local Python processes..."
    pkill -f "python.*run.py" || true
    echo "✅ Local processes stopped!"
else
    echo "ℹ️  No local Python processes found"
fi

echo "✅ All bot processes stopped!"
