import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Client configuration (for client_bot.py)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
TARGET_CHAT_ID = os.getenv('TARGET_CHAT_ID')

# Telegram Bot configuration (for bot.py)
BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_USERS_STR = os.getenv('ALLOWED_USERS_STR')
if ALLOWED_USERS_STR and ALLOWED_USERS_STR.isdigit():
    ALLOWED_USERS_STR = int(ALLOWED_USERS_STR)

# User management file path
USERS_FILE = os.path.join(os.path.dirname(__file__), 'allowed_users.json')

# Admin user ID (the first user who can add others)
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
if ADMIN_USER_ID and ADMIN_USER_ID.isdigit():
    ADMIN_USER_ID = int(ADMIN_USER_ID)

# Common configuration
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './downloads')

# Validate required environment variables for client_bot.py
if not API_ID:
    print("Warning: API_ID is not set. Required for client_bot.py")

if not API_HASH:
    print("Warning: API_HASH is not set. Required for client_bot.py")

if not PHONE_NUMBER:
    print("Warning: PHONE_NUMBER is not set. Required for client_bot.py")

if not TARGET_CHAT_ID:
    print("Warning: TARGET_CHAT_ID is not set. Required for client_bot.py")

# Validate required environment variables for bot.py
if not BOT_TOKEN:
    print("Warning: BOT_TOKEN is not set. Required for bot.py")

# Validate user management
if not ADMIN_USER_ID and not ALLOWED_USERS_STR:
    print("Warning: No ADMIN_USER_ID or ALLOWED_USERS_STR set. No one will be able to use the bot.")
    print("Set ADMIN_USER_ID in .env to enable user management features.")

if not ADMIN_USER_ID:
    print("Info: ADMIN_USER_ID not set. User management commands will be disabled.")

# Convert API_ID to int if it exists
if API_ID:
    try:
        API_ID = int(API_ID)
    except ValueError:
        print("Warning: API_ID must be a number")

# Convert TARGET_CHAT_ID to int if it's a number
if TARGET_CHAT_ID:
    try:
        TARGET_CHAT_ID = int(TARGET_CHAT_ID)
    except ValueError:
        # Keep as string if it's a username (starts with @)
        pass

# Download settings
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB limit for Telegram Client
DOWNLOAD_TIMEOUT = 1800  # 30 minutes timeout