import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Client configuration
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
TARGET_CHAT_ID = os.getenv('TARGET_CHAT_ID')

# User management
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

# Validate required environment variables
if not API_ID:
    print("Error: API_ID is required. Get it from https://my.telegram.org/apps")
    
if not API_HASH:
    print("Error: API_HASH is required. Get it from https://my.telegram.org/apps")
    
if not PHONE_NUMBER:
    print("Error: PHONE_NUMBER is required (e.g., +84123456789)")
    
if not TARGET_CHAT_ID:
    print("Error: TARGET_CHAT_ID is required (chat ID or @username)")

# User authorization info
if not ADMIN_USER_ID and not ALLOWED_USERS_STR:
    print("Warning: No ADMIN_USER_ID or ALLOWED_USERS_STR set.")
    print("Set ADMIN_USER_ID to enable user management features.")

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
DOWNLOAD_TIMEOUT = 1800  # 30 minutes