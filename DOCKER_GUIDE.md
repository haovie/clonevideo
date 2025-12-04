# Docker Deployment Guide

## Prerequisites

- Docker installed
- Docker Compose installed (optional, but recommended)
- `.env` file configured with your Telegram credentials

## Quick Start

### Method 1: Using Docker Compose (Recommended)

1. **Create `.env` file** with your credentials:
```bash
cp .env.example .env
# Edit .env with your values
```

2. **Build and run**:
```bash
docker-compose up -d
```

3. **View logs**:
```bash
docker-compose logs -f
```

4. **Stop the bot**:
```bash
docker-compose down
```

### Method 2: Using Docker directly

1. **Build the image**:
```bash
docker build -t telegram-video-bot .
```

2. **Run the container**:
```bash
docker run -d \
  --name telegram-bot \
  --env-file .env \
  -v $(pwd)/video_bot_session.session:/app/video_bot_session.session \
  -v $(pwd)/allowed_users.json:/app/allowed_users.json \
  --restart unless-stopped \
  telegram-video-bot
```

3. **View logs**:
```bash
docker logs -f telegram-bot
```

4. **Stop the container**:
```bash
docker stop telegram-bot
docker rm telegram-bot
```

## Environment Variables

Required variables in `.env`:

```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+84xxxxxxxxx
TARGET_CHAT_ID=-100xxxxxxxxx
ADMIN_USER_ID=your_user_id
DOWNLOAD_DIR=./downloads
```

## First Time Setup

On first run, you may need to authenticate:

1. **Check logs for authentication code**:
```bash
docker-compose logs -f
```

2. **Enter the code** when prompted (the bot will ask via Telegram)

3. **Session will be saved** in `video_bot_session.session` file

## Maintenance

### Update the bot

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Clean up old downloads

```bash
# Remove old downloads
rm -rf downloads/*
```

### Backup session file

```bash
# Important: backup your session to avoid re-authentication
cp video_bot_session.session video_bot_session.session.backup
```

## Troubleshooting

### Bot not starting

Check logs:
```bash
docker-compose logs
```

### Authentication issues

1. Stop the bot
2. Delete session file: `rm video_bot_session.session*`
3. Restart and authenticate again

### Out of disk space

Clean up Docker:
```bash
docker system prune -a
```

## Production Deployment

For production servers:

1. **Use systemd or supervisor** to manage docker-compose
2. **Set up log rotation** (already configured in docker-compose.yml)
3. **Monitor disk usage** for downloads folder
4. **Backup session file** regularly
5. **Use environment-specific .env files**

## Security Notes

- Never commit `.env` file
- Keep `video_bot_session.session` secure
- Use `ADMIN_USER_ID` to control access
- Regularly update dependencies
