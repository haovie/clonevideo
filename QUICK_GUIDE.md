# 🚀 Quick Guide - TikTok Photo Slideshows

## ✨ New Feature: TikTok Photo Slideshows

Your bot now automatically converts TikTok photo posts into beautiful video slideshows!

## 📱 How to Use

### 1. Find a TikTok Photo Post

Look for TikTok posts that show multiple photos (slideshow format). These URLs typically contain `/photo/`:

```
https://www.tiktok.com/@username/photo/1234567890
```

### 2. Send URL to Bot

Simply paste the TikTok photo URL into your Telegram chat with the bot.

### 3. Bot Processing

The bot will automatically:

- 📸 Download all images from the slideshow
- 🎵 Extract the original audio
- 🎬 Create a high-quality video (TikTok format 9:16)
- ⚡ Add smooth transitions between images

### 4. Choose Action

After processing, use commands:

- `/forward` - Send to your target chat/group
- `/download` - Download to your personal chat (if authorized)
- `/cancel` - Cancel the operation

**💡 First Time Setup:**
- Use `/get_user_id` to get your User ID
- Ask admin to add you with `/add_user <your_id>`
- Or set yourself as admin in `.env` with `ADMIN_USER_ID=<your_id>`

## 🎯 What You Get

- **Format**: MP4 video (1080x1920 TikTok format)
- **Audio**: Original TikTok audio preserved
- **Quality**: High-quality encoding optimized for mobile
- **Transitions**: Smooth fade effects between images
- **Duration**: Automatically calculated based on audio length

## 🔍 Example URLs That Work

```
✅ https://www.tiktok.com/@tngoclam10092007/photo/7496484372200246535
✅ https://vm.tiktok.com/photo/ZGeFpqLTJ/
✅ https://www.tiktok.com/@user/photo/1234567890123456789
```

## ⚠️ Requirements

- **FFmpeg**: Must be installed on the server
- **Gallery-dl**: Automatically installed with the bot
- **Internet**: Stable connection for downloading images

## 🛠️ Technical Details

- **Resolution**: 1080x1920 (9:16 aspect ratio)
- **Video Codec**: H.264
- **Audio Codec**: AAC 44.1kHz stereo
- **Frame Rate**: 30fps
- **File Size**: Typically 0.5-50MB depending on content

## 👥 User Management (Admins)

**Admin Commands:**
```
/add_user 123456789     # Add new user
/remove_user 123456789  # Remove user
/list_users             # Show all users
```

**Setup Steps:**
1. Set `ADMIN_USER_ID=your_id` in `.env`
2. Restart bot
3. Use commands to manage users

## 📞 Support

If you encounter issues:

1. Check that the URL contains `/photo/`
2. Ensure stable internet connection
3. Try again after a few minutes
4. Contact bot administrator if problems persist
5. **Authorization issues**: Ask admin to add your User ID

## 🎉 Enjoy!

Transform your favorite TikTok photo collections into shareable videos with just one command!
