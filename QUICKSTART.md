# 🚀 Quick Start Guide - Telegram Video Bot

## 📋 Prerequisites

- Python 3.9+ or Docker
- Telegram account
- FFmpeg installed (for video processing)

## ⚡ Fast Setup (5 minutes)

### Step 1: Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Login with your phone number
3. Create a new application
4. Copy your `API_ID` and `API_HASH`

### Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your values
nano .env
```

Required values:
```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE_NUMBER=+84xxxxxxxxx
TARGET_CHAT_ID=-100xxxxxxxxx
ADMIN_USER_ID=your_user_id
```

### Step 3: Run the Bot

#### Option A: Docker (Recommended for production)
```bash
# Start bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down
```

#### Option B: Python (For development)
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python3 run.py
```

#### Option C: Use start script
```bash
chmod +x start.sh
./start.sh
```

## 🎯 First Time Authentication

On first run, you'll need to authenticate:

1. Bot will send a code to your Telegram
2. Enter the code when prompted
3. Session will be saved automatically
4. Next time, no authentication needed!

## 📱 How to Use

### Get Your User ID
Send to the bot: `/get_user_id`

### Download Video
1. Send video URL to the bot
2. Wait for info
3. Send `/forward` to download and forward to target chat

### Cancel Task
Send: `/cancel`

### Admin Commands (if you're admin)
- `/add_user 123456789` - Add user
- `/remove_user 123456789` - Remove user
- `/list_users` - View all users

## 🎬 Supported Platforms

✅ YouTube
✅ TikTok (including photo slideshows)
✅ Twitter/X
✅ Instagram
✅ Facebook
✅ Vimeo
✅ And many more!

## 🎵 Features

- ✅ Files up to 2GB
- ✅ High-quality audio (320kbps)
- ✅ TikTok photo slideshows
- ✅ Cancel anytime
- ✅ Fast and stable
- ✅ User management

## 🐳 Docker Commands Cheat Sheet

```bash
# Start bot
docker-compose up -d

# View logs
docker-compose logs -f

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# View running containers
docker-compose ps

# Update and restart
git pull && docker-compose up -d --build
```

## 🛠️ Troubleshooting

### Bot not responding?
```bash
# Check logs
docker-compose logs -f
# or
tail -f bot.log
```

### Authentication error?
```bash
# Delete session and re-authenticate
rm video_bot_session.session*
docker-compose restart
```

### Out of disk space?
```bash
# Clean downloads
rm -rf downloads/*

# Clean Docker
docker system prune -a
```

### FFmpeg not found?
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Docker: already included!
```

## 📊 Monitoring

### Check bot status
```bash
docker-compose ps
```

### View resource usage
```bash
docker stats telegram-video-bot
```

### Check disk usage
```bash
du -sh downloads/
```

## 🔒 Security Tips

1. **Never share** your `.env` file
2. **Backup** your `video_bot_session.session` file
3. **Use ADMIN_USER_ID** to control access
4. **Keep Docker updated** for security patches
5. **Monitor logs** for suspicious activity

## 📚 More Documentation

- `README.md` - Full documentation
- `DOCKER_GUIDE.md` - Docker deployment guide
- `CHANGELOG_CLEANUP.md` - Recent changes
- `CONFIGURATION.md` - Configuration options

## 💡 Pro Tips

1. Use Docker for production - it's more stable
2. Set up log rotation to prevent disk fill
3. Clean downloads folder regularly
4. Backup session file before updates
5. Use systemd to auto-start Docker on boot

## ❓ Getting Help

1. Check logs first
2. Read error messages carefully
3. Search issues on GitHub
4. Check Telegram API status
5. Verify your credentials

## 🎉 You're Ready!

Your bot should now be running and ready to download videos!

Send a video URL to test it out. 🚀

---

**Need help?** Check the full documentation in README.md
