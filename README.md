# Telegram Video Client Bot

Telegram client bot for downloading videos from various platforms using Telethon with advanced features.

## ✨ Features

- 🎬 Download videos from YouTube, TikTok, Instagram, Facebook, Twitter/X, Vimeo, etc.
- 📸 **NEW: TikTok Photo Slideshows** - Automatically download all images from TikTok photo posts and create video slideshows with audio
- 📤 Upload files up to 2GB (no 50MB Bot API limitation)
- 🔄 Auto-retry with browser cookies for 403 errors
- 📊 Real-time upload progress
- 🧹 Automatic cleanup
- ⚡ Better upload speed and reliability
- ❌ Cancel tasks anytime
- 🎯 Forward to target chat or download to personal chat

## 🚀 Quick Setup

### 1. Install system dependencies

**FFmpeg (Required for video processing and TikTok slideshows):**

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 2. Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 2. Get Telegram API credentials

1. Go to https://my.telegram.org/apps
2. Create new application
3. Note down `api_id` and `api_hash`

### 3. Configure client

Create `.env` file:

```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+84xxxxxxxxx
TARGET_CHAT_ID=your_target_chat_id
DOWNLOAD_DIR=./downloads

# User Management (New!)
ADMIN_USER_ID=your_user_id      # Admin can manage other users
ALLOWED_USERS_STR=user_id       # Legacy support (optional)
```

### 4. Run client

```bash
python3 run.py
```

## 📋 Configuration

- `API_ID` and `API_HASH`: From my.telegram.org/apps
- `PHONE_NUMBER`: Your phone number in international format
- `TARGET_CHAT_ID`: Chat ID for auto-forwarding videos
- `DOWNLOAD_DIR`: Directory to store downloads (default: ./downloads)
- `ADMIN_USER_ID`: User ID of admin who can manage other users (important!)
- `ALLOWED_USERS_STR`: Legacy user ID for backward compatibility (optional)

### 🆕 User Management

The bot now supports flexible user management through commands:

**Admin Commands:**
- `/add_user <user_id>` - Add user to allowed list
- `/remove_user <user_id>` - Remove user from list  
- `/list_users` - Show all allowed users
- `/get_user_id` - Get your user ID

**Example:**
```
/add_user 123456789
/remove_user 987654321
/list_users
```

**User Sources (in priority order):**
1. `ADMIN_USER_ID` - Always allowed, can manage others
2. `ALLOWED_USERS_STR` - From .env file
3. `allowed_users.json` - Added via commands

### Getting TARGET_CHAT_ID

**For groups:**

1. Add client to group
2. Send a message
3. Check logs for chat ID (negative number)

**For channels:**

1. Add client as admin
2. Use channel username (e.g., @mychannel) or numeric ID

### Phone verification

- First run requires phone verification
- Enter verification code when prompted
- Session will be saved for future runs

## 🎯 Usage

### Commands

- `/start` - Show welcome message
- `/help` - Show help
- `/forward` - Forward last video to target chat
- `/download` - Download last video to your personal chat (restricted users only)
- `/cancel` - Cancel all your active tasks
- `/get_user_id` - Get your Telegram user ID

### Basic Usage

1. Start bot: `/start`
2. Send video URL in chat
3. Use `/forward` to send to target chat
4. Use `/download` to download to your device (if authorized)
5. Use `/cancel` to stop any active download/upload

## 🔧 Advantages of Client Bot

| Feature          | Bot API | Client API |
| ---------------- | ------- | ---------- |
| File size limit  | 50MB    | 2GB        |
| Upload speed     | Slower  | Faster     |
| Timeout errors   | Common  | Rare       |
| Task cancellation| No      | Yes        |
| Better reliability| No     | Yes        |

## 📁 Project Structure

```
telegram-video-client-bot/
├── client_bot.py      # Main client bot using Telethon
├── downloader.py      # Video download logic
├── config.py          # Configuration
├── utils.py           # Utility functions
├── run.py             # Bot runner
├── setup.py           # Setup script
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## 🛠️ Troubleshooting

- **"Invalid phone number"**: Use international format: +84xxxxxxxxx
- **"Could not find the input entity"**: Check TARGET_CHAT_ID is correct
- **"Session file error"**: Delete `video_bot_session.session` file and re-authenticate
- **"Download failed"**: Video might be geo-blocked or private
- **"Timeout error"**: Try again or check internet connection

## 📸 TikTok Photo Slideshow Feature

The bot now supports TikTok photo/slideshow posts! When you send a TikTok URL containing `/photo/`, the bot will:

1. **Download all images** from the slideshow using `gallery-dl`
2. **Extract audio** from the original post
3. **Create a high-quality video** combining images with audio
4. **Optimize for TikTok format** (9:16 aspect ratio, 1080x1920 resolution)
5. **Add smooth transitions** between images

### Supported TikTok URLs:
- `https://www.tiktok.com/@user/photo/123456789`
- `https://vm.tiktok.com/photo/123456789`
- Any TikTok URL containing `/photo/`

### Features:
- 🎵 Preserves original audio from TikTok post
- 🖼️ Downloads all images in high quality
- 🎬 Creates smooth video transitions
- 📱 Optimized for mobile viewing (TikTok format)
- ⚡ Automatic fallback to yt-dlp if gallery-dl fails

## 📝 Dependencies

- `telethon` - Telegram Client API
- `yt-dlp` - Video downloader
- `gallery-dl` - Image gallery downloader (for TikTok photos)
- `python-dotenv` - Environment variables
- `ffmpeg` - Video processing (system dependency)

## 🔒 Security

- Keep `.env` file secure
- Don't share API credentials
- Session files contain authentication data

## 📄 License

MIT License
