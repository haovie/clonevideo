"""
Utility functions for the Telegram Video Bot
"""

import os
import re
import logging
from typing import Optional, List
from urllib.parse import urlparse
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs}s"

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    urls = url_pattern.findall(text)
    return [url for url in urls if is_valid_url(url)]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def get_video_platform(url: str) -> Optional[str]:
    """Identify video platform from URL with enhanced TikTok detection"""
    domain_mapping = {
        'youtube.com': 'YouTube',
        'youtu.be': 'YouTube',
        'tiktok.com': 'TikTok',
        'instagram.com': 'Instagram',
        'facebook.com': 'Facebook',
        'twitter.com': 'Twitter',
        'x.com': 'Twitter/X',
        'vimeo.com': 'Vimeo',
        'dailymotion.com': 'Dailymotion',
        'twitch.tv': 'Twitch'
    }
    
    # Enhanced TikTok photo detection
    if 'tiktok.com' in url:
        if '/photo/' in url or 'slideshow' in url.lower():
            return 'TikTok Photos'
        else:
            return 'TikTok'
    
    try:
        domain = urlparse(url).netloc.lower()
        for key, platform in domain_mapping.items():
            if key in domain:
                return platform
    except Exception:
        pass
    
    return None

def is_valid_video_url(url: str) -> bool:
    """Check if URL is from a supported video platform"""
    if not is_valid_url(url):
        return False
    
    # Get the platform - if it returns None, it's not a supported platform
    platform = get_video_platform(url)
    return platform is not None

def is_spam_url(url: str) -> bool:
    """Check if URL appears to be spam/promotional content"""
    spam_indicators = [
        'taphoammo.net',
        'gian-hang',
        'tai-khoan',
        'pro-',
        'ban-nick',
        'mua-ban',
        'kiem-tien',
        'hack-',
        'mod-apk',
        'download-',
        'crack-',
        'free-fire',
        'pubg-',
        'lien-quan'
    ]
    
    url_lower = url.lower()
    for indicator in spam_indicators:
        if indicator in url_lower:
            return True
    
    return False

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a text progress bar"""
    if total == 0:
        return "█" * length
    
    filled_length = int(length * current // total)
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = round(100 * current / total, 1)
    
    return f"{bar} {percentage}%"

def validate_chat_id(chat_id: str) -> bool:
    """Validate Telegram chat ID format"""
    try:
        # Chat ID can be a number (positive for channels, negative for groups)
        # or a username starting with @
        if chat_id.startswith('@'):
            return len(chat_id) > 1 and chat_id[1:].replace('_', '').isalnum()
        else:
            int(chat_id)
            return True
    except ValueError:
        return False

def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# User management functions
def load_allowed_users():
    """Load allowed users from JSON file"""
    from config import USERS_FILE
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('allowed_users', []))
        return set()
    except Exception as e:
        print(f"Error loading users file: {e}")
        return set()

def save_allowed_users(users_set):
    """Save allowed users to JSON file"""
    from config import USERS_FILE
    
    try:
        data = {
            'allowed_users': list(users_set),
            'last_updated': datetime.now().isoformat()
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving users file: {e}")
        return False

def add_allowed_user(user_id):
    """Add a user to allowed users list"""
    users = load_allowed_users()
    users.add(user_id)
    return save_allowed_users(users)

def remove_allowed_user(user_id):
    """Remove a user from allowed users list"""
    users = load_allowed_users()
    users.discard(user_id)
    return save_allowed_users(users)

def is_user_allowed(user_id):
    """Check if user is allowed (combines file-based and env-based checks)"""
    from config import ALLOWED_USERS_STR, ADMIN_USER_ID
    
    # Admin is always allowed
    if ADMIN_USER_ID and user_id == ADMIN_USER_ID:
        return True
    
    # Check environment variable setting
    if ALLOWED_USERS_STR:
        if isinstance(ALLOWED_USERS_STR, int):
            if user_id == ALLOWED_USERS_STR:
                return True
        elif hasattr(ALLOWED_USERS_STR, '__iter__'):
            if user_id in ALLOWED_USERS_STR:
                return True
    
    # Check file-based users
    file_users = load_allowed_users()
    return user_id in file_users

def get_all_allowed_users():
    """Get all allowed users from both sources"""
    from config import ALLOWED_USERS_STR, ADMIN_USER_ID
    
    all_users = set()
    
    # Add admin
    if ADMIN_USER_ID:
        all_users.add(ADMIN_USER_ID)
    
    # Add from environment
    if ALLOWED_USERS_STR:
        if isinstance(ALLOWED_USERS_STR, int):
            all_users.add(ALLOWED_USERS_STR)
        elif hasattr(ALLOWED_USERS_STR, '__iter__'):
            all_users.update(ALLOWED_USERS_STR)
    
    # Add from file
    file_users = load_allowed_users()
    all_users.update(file_users)
    
    return all_users