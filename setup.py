#!/usr/bin/env python3
"""
Setup script for Telegram Video Client Bot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print header text"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_step(text):
    """Print step text"""
    print(f"\n>> {text}")

def run_command(command):
    """Run shell command"""
    print(f"$ {command}")
    return subprocess.run(command, shell=True, check=True)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    if env_path.exists():
        print("⚠️  .env file already exists. Skipping...")
        return
    
    print_step("Creating .env file for Client Bot")
    
    api_id = input("Enter your API ID from my.telegram.org: ").strip()
    api_hash = input("Enter your API Hash from my.telegram.org: ").strip()
    phone = input("Enter your phone number (e.g. +84123456789): ").strip()
    target_chat = input("Enter target chat ID or username: ").strip()
    allowed_users = input("Enter allowed user IDs (comma separated, optional): ").strip()
    
    with open(".env", "w") as f:
        f.write("# Client Bot Configuration\n")
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
        f.write(f"PHONE_NUMBER={phone}\n")
        f.write(f"TARGET_CHAT_ID={target_chat}\n")
        f.write("DOWNLOAD_DIR=./downloads\n")
        if allowed_users:
            f.write(f"ALLOWED_USERS={allowed_users}\n")
    
    print("✅ .env file created successfully!")

def main():
    """Main setup function"""
    print_header("Telegram Video Client Bot Setup")
    
    # Create downloads directory
    print_step("Creating downloads directory")
    os.makedirs("downloads", exist_ok=True)
    
    # Install requirements
    print_step("Installing dependencies")
    try:
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please install manually:")
        print(f"{sys.executable} -m pip install -r requirements.txt")
    
    # Create .env file
    create_env_file()
    
    print_header("Setup Complete!")
    print("""
To run the bot:

    python3 run.py

Features:
- Supports files up to 2GB
- Can cancel tasks anytime
- Better upload reliability
- Works with multiple video platforms

For more information, read the README.md file.
""")

if __name__ == "__main__":
    main()