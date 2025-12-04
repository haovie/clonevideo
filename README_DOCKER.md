# 🐳 Telegram Video Bot - Docker Edition

> **Production-ready Telegram Client Bot for downloading videos with Docker support**

## 🎯 Quick Deploy (2 commands)

```bash
cp .env.example .env && nano .env
docker-compose up -d
```

## ✨ Features

- 📦 **2GB File Support** - No 50MB Bot API limit
- 🎵 **High Quality Audio** - 320kbps bitrate
- 🖼️ **TikTok Photos** - Slideshow creation
- 🚫 **Cancel Anytime** - Stop downloads
- 👥 **User Management** - Admin controls
- 🐳 **Docker Ready** - One-command deployment

## 📋 What You Need

1. Telegram API credentials from https://my.telegram.org/apps
2. Docker & Docker Compose installed
3. Your phone number
4. Target chat ID

## 🚀 Step-by-Step Setup

### 1. Get Telegram Credentials

Visit https://my.telegram.org/apps:
- Login with your phone
- Create new application
- Copy `API_ID` and `API_HASH`

### 2. Configure

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required configuration:
```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+84xxxxxxxxx
TARGET_CHAT_ID=-100xxxxxxxxx
ADMIN_USER_ID=your_user_id
```

### 3. Deploy

```bash
# Start bot
docker-compose up -d

# View logs (important for first-time auth)
docker-compose logs -f
```

### 4. First Authentication

When you run for the first time:
1. Bot sends code to your Telegram
2. Enter code when prompted in logs
3. Session saved automatically
4. Future runs won't need authentication

## 🎮 Usage

### Basic Commands

```
/start          - Show welcome message
/help           - Show help
/get_user_id    - Get your user ID
/cancel         - Cancel running tasks
```

### Admin Commands (if configured)

```
/add_user <id>     - Add allowed user
/remove_user <id>  - Remove user
/list_users        - List all users
```

### Download Videos

1. **Send video URL** to bot
2. **Wait for info** (title, size, duration)
3. **Send `/forward`** to download and forward to target chat

### Supported Platforms

✅ YouTube  
✅ TikTok (videos + photo slideshows)  
✅ Twitter/X  
✅ Instagram  
✅ Facebook  
✅ Vimeo  
✅ Dailymotion  
✅ And many more via yt-dlp!

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Update and restart
git pull && docker-compose up -d --build

# Check status
docker-compose ps

# View resource usage
docker stats telegram-video-bot
```

## 📁 Project Structure

```
telegram-video-bot/
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker orchestration
├── .dockerignore          # Build optimization
├── .env                   # Your credentials (gitignored)
├── .env.example          # Template
│
├── run.py                # Entry point
├── client_bot.py         # Main bot logic
├── downloader.py         # Video downloads
├── audio_enhancer.py     # Audio processing
├── utils.py              # Utilities
├── config.py             # Configuration
├── requirements.txt      # Dependencies
│
├── start.sh             # Universal start script
├── stop.sh              # Universal stop script
│
└── Documentation/
    ├── QUICKSTART.md           # 5-min setup
    ├── DOCKER_GUIDE.md         # Docker details
    ├── DEPLOYMENT_SUMMARY.md   # Overview
    └── CHANGELOG_CLEANUP.md    # Changes log
```

## 🔧 Configuration Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_ID` | ✅ | Telegram API ID | `12345678` |
| `API_HASH` | ✅ | Telegram API Hash | `abc123def456...` |
| `PHONE_NUMBER` | ✅ | Your phone (with country code) | `+84123456789` |
| `TARGET_CHAT_ID` | ✅ | Where to forward videos | `-1001234567890` |
| `ADMIN_USER_ID` | ⚠️ | Admin for user management | `123456789` |
| `ALLOWED_USERS_STR` | ❌ | Additional allowed users | `123,456,789` |
| `DOWNLOAD_DIR` | ❌ | Download location | `./downloads` |

## 🛠️ Troubleshooting

### Bot won't start

```bash
# Check logs for errors
docker-compose logs

# Verify .env file
cat .env

# Restart fresh
docker-compose down
docker-compose up -d
```

### Authentication failed

```bash
# Remove old session
rm video_bot_session.session*

# Restart and re-authenticate
docker-compose restart
docker-compose logs -f
```

### Downloads not working

```bash
# Check FFmpeg (included in Docker)
docker-compose exec telegram-bot ffmpeg -version

# Check disk space
df -h
docker system df
```

### Out of disk space

```bash
# Clean old downloads
rm -rf downloads/*

# Clean Docker
docker system prune -a
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Max file size | 2GB |
| Audio quality | 320kbps |
| Startup time | ~5 seconds |
| Memory usage | ~100-200MB |
| Docker image | ~450MB |
| CPU usage | Low (idle), Medium (download) |

## 🔒 Security

### Best Practices

1. ✅ Never commit `.env` file
2. ✅ Keep `video_bot_session.session` secure
3. ✅ Use `ADMIN_USER_ID` for access control
4. ✅ Backup session file regularly
5. ✅ Keep Docker and dependencies updated
6. ✅ Use strong permissions on config files

### Backup Important Files

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_${DATE}.tar.gz \
    video_bot_session.session* \
    allowed_users.json \
    .env
```

## 📈 Monitoring

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs from specific time
docker-compose logs --since 10m
```

### Resource Monitoring

```bash
# Container stats
docker stats telegram-video-bot

# Disk usage
du -sh downloads/
docker system df
```

## 🔄 Updates

### Update Bot Code

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Update Dependencies

```bash
# Edit requirements.txt
nano requirements.txt

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

## 🎓 Advanced Usage

### Custom Download Directory

```bash
# In .env
DOWNLOAD_DIR=/path/to/custom/dir

# Restart
docker-compose restart
```

### Multiple Bot Instances

```bash
# Create separate directory
cp -r telegram-bot telegram-bot-2
cd telegram-bot-2

# Edit .env with different credentials
nano .env

# Start with different project name
docker-compose -p bot2 up -d
```

### Auto-start on Boot

```bash
# Add to systemd (Linux)
sudo nano /etc/systemd/system/telegram-bot.service

[Unit]
Description=Telegram Video Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target

# Enable
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## 📚 Documentation

- **Quick Start**: `QUICKSTART.md` - 5-minute setup guide
- **Docker Guide**: `DOCKER_GUIDE.md` - Detailed Docker info
- **Deployment**: `DEPLOYMENT_SUMMARY.md` - Production checklist
- **Changes**: `CHANGELOG_CLEANUP.md` - What's new

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is for personal use. Respect video platforms' terms of service.

## ⚠️ Disclaimer

This bot is for downloading videos you have rights to download. Always respect:
- Copyright laws
- Platform terms of service
- Content creators' rights
- Privacy regulations

## 💡 Tips & Tricks

1. **Performance**: Use SSD for downloads
2. **Reliability**: Enable auto-restart in docker-compose
3. **Monitoring**: Set up log aggregation
4. **Backup**: Automate session backup
5. **Updates**: Subscribe to repository for updates

## 🆘 Getting Help

1. **Check logs first**: `docker-compose logs -f`
2. **Read documentation**: Start with `QUICKSTART.md`
3. **Common issues**: See troubleshooting section
4. **Verify credentials**: Double-check `.env` file
5. **Test FFmpeg**: `docker-compose exec telegram-bot ffmpeg -version`

## 🎉 Success Checklist

- [ ] Docker installed and running
- [ ] `.env` file configured
- [ ] Bot started with `docker-compose up -d`
- [ ] Authenticated successfully
- [ ] Tested with a video URL
- [ ] Video downloaded and forwarded
- [ ] Session persists after restart

---

## 🚀 Ready to Deploy?

```bash
# 1. Configure
cp .env.example .env && nano .env

# 2. Deploy
docker-compose up -d

# 3. Watch logs
docker-compose logs -f

# 4. Test it!
# Send a video URL to your bot
```

**That's it! Your bot is now running! 🎊**

For detailed setup, read `QUICKSTART.md`  
For production deployment, read `DOCKER_GUIDE.md`

---

**Made with ❤️ for easy video downloading**
