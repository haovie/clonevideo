#!/usr/bin/env python3
"""
Optimized Telegram Video Bot using Telethon Client
Supports files up to 2GB and better upload reliability with cancellation support
"""

import logging
import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo
from downloader import VideoDownloader
from audio_enhancer import AudioEnhancer
from config import API_ID, API_HASH, PHONE_NUMBER, TARGET_CHAT_ID, ADMIN_USER_ID
from utils import (extract_urls_from_text, format_file_size, format_duration, 
                   get_video_platform, is_valid_video_url, is_spam_url,
                   is_user_allowed, add_allowed_user, remove_allowed_user, get_all_allowed_users, load_allowed_users)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramVideoClient:
    def __init__(self):
        self.client = TelegramClient('video_bot_session', API_ID, API_HASH)
        self.downloader = VideoDownloader()
        self.active_tasks = {}  # Store active download/upload tasks
        self.task_counter = 0
        
    async def start(self):
        """Start the client"""
        await self.client.start(phone=PHONE_NUMBER)
        logger.info("Client started successfully!")
        
        # Helper function to wrap event handlers with error handling
        def safe_handler(handler_func):
            async def wrapped_handler(event):
                try:
                    await handler_func(event)
                except Exception as e:
                    logger.error(f"Error in handler {handler_func.__name__}: {e}")
                    try:
                        await event.respond(f"❌ Đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.")
                    except Exception:
                        # If we can't respond, just log it
                        pass
            return wrapped_handler
        
        # Register event handlers
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await safe_handler(self.handle_start)(event)
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await safe_handler(self.handle_help)(event)
        
        @self.client.on(events.NewMessage(pattern='/cancel'))
        async def cancel_handler(event):
            await safe_handler(self.handle_cancel)(event)
        
        @self.client.on(events.NewMessage(pattern='/forward'))
        async def forward_handler(event):
            await safe_handler(self.handle_forward_command)(event)
        
        @self.client.on(events.NewMessage(pattern='/download'))
        async def download_handler(event):
            await safe_handler(self.handle_download_command)(event)

        @self.client.on(events.NewMessage(pattern='/down_photos'))
        async def photos_handler(event):
            await safe_handler(self.handle_photos_command)(event)

        @self.client.on(events.NewMessage(pattern='/fowd_photos'))
        async def photos_forward_handler(event):
            await safe_handler(self.handle_photos_forward_command)(event)
            
        @self.client.on(events.NewMessage(pattern='/get_user_id'))
        async def get_user_id_handler(event):
            await safe_handler(self.handle_get_user_id)(event)
        
        @self.client.on(events.NewMessage(pattern='/add_user'))
        async def add_user_handler(event):
            await safe_handler(self.handle_add_user)(event)
        
        @self.client.on(events.NewMessage(pattern='/remove_user'))
        async def remove_user_handler(event):
            await safe_handler(self.handle_remove_user)(event)
        
        @self.client.on(events.NewMessage(pattern='/list_users'))
        async def list_users_handler(event):
            await safe_handler(self.handle_list_users)(event)
        
        @self.client.on(events.NewMessage(func=lambda e: not e.message.text.startswith('/')))
        async def message_handler(event):
            await safe_handler(self.handle_message)(event)
        
        
        logger.info("Event handlers registered. Bot is ready!")
    
    async def handle_start(self, event):
        """Handle /start command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        if not self.is_authorized(event.sender_id):
            # await event.respond("❌ Bạn không có quyền sử dụng lệnh này.")
            return
            
        user_id = event.sender_id
        logger.info(f"User {user_id} started the bot")
        
        welcome_text = """
🎬 **Video Download Bot - Enhanced Audio Quality**

✨ **Tính năng xịn xò:**
• Hỗ trợ file lên đến 2GB
• Nhanh và ổn định
• Hỗ trợ nhiều nền tảng video
• Hỗ trợ TikTok Photo Slideshows (nghĩa là tạo video từ các hình ảnh trong URL + audio luôn)
• **Có thể hủy tác vụ**
• 🎵 **ÂM THANH CHẤT LƯỢNG CAO**: 320kbps, âm lượng đã được tăng cường và cân bằng!

**Cách sử dụng:**
1. Gửi URL video vào chat
2. Chọn lệnh để lấy video

**Lệnh cơ bản:**
• `/get_user_id` - Lấy ID của bạn
• `/cancel` - Hủy tác vụ đang chạy

**Nền tảng hỗ trợ:**
YouTube, TikTok (bao gồm Photo Slideshows), Twitter/X, Vimeo, v.v.
        """
        await event.respond(welcome_text)
    
    async def handle_help(self, event):
        """Handle /help command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        if not self.is_authorized(event.sender_id):
            # await event.respond("❌ Bạn không có quyền sử dụng lệnh này.")
            return
            
        user_id = event.sender_id
        is_admin = self.is_admin(user_id)
        
        help_text = """
🆘 **Trợ giúp**

**Lệnh cơ bản:**
• `/start` - Khởi động bot
• `/help` - Hiển thị trợ giúp
• `/cancel` - Hủy tất cả tác vụ đang chạy
• `/get_user_id` - Lấy ID người dùng của bạn

**Sử dụng:**
1. Gửi URL video vào chat
2. Bot tự động tải và chuyển tiếp
3. Hỗ trợ file lên đến 2GB

**Ưu điểm:**
• Không giới hạn 50MB như Bot API
• Upload nhanh và ổn định
• Ít lỗi timeout
• Có thể hủy tác vụ bất kỳ lúc nào
• **Hỗ trợ TikTok Photo Slideshows (Nghĩa là tạo video từ các hình ảnh trong URL + audio luôn)**
• 🎵 **ÂM THANH NÂNG CAP**: 320kbps bitrate, âm lượng +250%, EQ tối ưu, loại bỏ nhiễu
        """
        
        if is_admin:
            help_text += """

👑 **Lệnh quản trị (chỉ admin):**
• `/add_user <user_id>` - Thêm user được phép sử dụng bot
• `/remove_user <user_id>` - Xóa user khỏi danh sách
• `/list_users` - Xem danh sách users được phép
            """
        await event.respond(help_text)
    
    async def handle_get_user_id(self, event):
        """Handle /get_user_id command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
            
        user_id = event.sender_id
        username = event.sender.username if hasattr(event.sender, 'username') and event.sender.username else "Không có username"
        first_name = event.sender.first_name if hasattr(event.sender, 'first_name') and event.sender.first_name else "Không có tên"
        
        user_info = f"""
🆔 **Thông tin người dùng:**

👤 **User ID:** `{user_id}`
📛 **Username:** @{username}
👋 **Tên:** {first_name}
        """
        
        await event.respond(user_info)
    
    async def handle_add_user(self, event):
        """Handle /add_user command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        # Only admin can add users
        if not self.is_admin(event.sender_id):
            await event.respond("❌ Chỉ admin mới có thể thêm user.")
            return
        
        try:
            # Extract user_id from command
            command_text = event.message.text.strip()
            parts = command_text.split()
            
            if len(parts) != 2:
                await event.respond("""
❌ **Sai cú pháp!**

**Cách sử dụng:**
`/add_user <user_id>`

**Ví dụ:**
`/add_user 123456789`

💡 Dùng `/get_user_id` để lấy ID của user.
                """)
                return
            
            try:
                user_id_to_add = int(parts[1])
            except ValueError:
                await event.respond("❌ User ID phải là số nguyên.")
                return
            
            # Check if user is already allowed
            if is_user_allowed(user_id_to_add):
                await event.respond(f"ℹ️ User `{user_id_to_add}` đã có trong danh sách.")
                return
            
            # Add user
            if add_allowed_user(user_id_to_add):
                await event.respond(f"✅ Đã thêm user `{user_id_to_add}` vào danh sách được phép.")
                logger.info(f"Admin {event.sender_id} added user {user_id_to_add}")
            else:
                await event.respond("❌ Không thể lưu danh sách user. Vui lòng thử lại.")
                
        except Exception as e:
            logger.error(f"Error in add_user command: {e}")
            await event.respond(f"❌ Lỗi khi thêm user: {str(e)}")
    
    async def handle_remove_user(self, event):
        """Handle /remove_user command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        # Only admin can remove users
        if not self.is_admin(event.sender_id):
            await event.respond("❌ Chỉ admin mới có thể xóa user.")
            return
        
        try:
            # Extract user_id from command
            command_text = event.message.text.strip()
            parts = command_text.split()
            
            if len(parts) != 2:
                await event.respond("""
❌ **Sai cú pháp!**

**Cách sử dụng:**
`/remove_user <user_id>`

**Ví dụ:**
`/remove_user 123456789`
                """)
                return
            
            try:
                user_id_to_remove = int(parts[1])
            except ValueError:
                await event.respond("❌ User ID phải là số nguyên.")
                return
            
            # Check if trying to remove admin
            if user_id_to_remove == ADMIN_USER_ID:
                await event.respond("❌ Không thể xóa admin khỏi danh sách.")
                return
            
            # Check if user exists in file-based list
            file_users = load_allowed_users()
            if user_id_to_remove not in file_users:
                await event.respond(f"ℹ️ User `{user_id_to_remove}` không có trong danh sách file (có thể trong env).")
                return
            
            # Remove user
            if remove_allowed_user(user_id_to_remove):
                await event.respond(f"✅ Đã xóa user `{user_id_to_remove}` khỏi danh sách.")
                logger.info(f"Admin {event.sender_id} removed user {user_id_to_remove}")
            else:
                await event.respond("❌ Không thể lưu danh sách user. Vui lòng thử lại.")
                
        except Exception as e:
            logger.error(f"Error in remove_user command: {e}")
            await event.respond(f"❌ Lỗi khi xóa user: {str(e)}")
    
    async def handle_list_users(self, event):
        """Handle /list_users command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        # Only admin can list users
        if not self.is_admin(event.sender_id):
            await event.respond("❌ Chỉ admin mới có thể xem danh sách user.")
            return
        
        try:
            all_users = get_all_allowed_users()
            
            if not all_users:
                await event.respond("📝 **Danh sách users:**\n\nℹ️ Chưa có user nào được phép sử dụng.")
                return
            
            # Separate users by source
            from config import ALLOWED_USERS_STR
            file_users = load_allowed_users()
            env_users = set()
            
            if ALLOWED_USERS_STR:
                if isinstance(ALLOWED_USERS_STR, int):
                    env_users.add(ALLOWED_USERS_STR)
                elif hasattr(ALLOWED_USERS_STR, '__iter__'):
                    env_users.update(ALLOWED_USERS_STR)
            
            response = "📝 **Danh sách users được phép:**\n\n"
            
            # Admin
            if ADMIN_USER_ID:
                response += f"👑 **Admin:** `{ADMIN_USER_ID}`\n\n"
            
            # Environment users
            if env_users:
                response += "🔧 **Từ Environment (.env):**\n"
                for user_id in sorted(env_users):
                    if user_id != ADMIN_USER_ID:  # Don't duplicate admin
                        response += f"• `{user_id}`\n"
                response += "\n"
            
            # File users
            if file_users:
                response += "📁 **Từ File (có thể quản lý):**\n"
                for user_id in sorted(file_users):
                    if user_id != ADMIN_USER_ID and user_id not in env_users:  # Don't duplicate
                        response += f"• `{user_id}`\n"
            
            response += f"\n📊 **Tổng cộng:** {len(all_users)} users"
            
            await event.respond(response)
            
        except Exception as e:
            logger.error(f"Error in list_users command: {e}")
            await event.respond(f"❌ Lỗi khi lấy danh sách user: {str(e)}")
    
    async def handle_message(self, event):
        """Handle incoming messages with URLs"""
        if not event.message or not event.message.text:
            return  # Skip if no message or text
            
        if event.message.text.startswith('/'):
            return  # Skip commands
        
        # Check if message is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        user_id = event.sender_id
        
        urls = extract_urls_from_text(event.message.text)
        if not urls:
            return  # No URLs found
        
        # Check if user already has an active task for this URL to prevent duplicates
        for task_id, task_info in self.active_tasks.items():
            if task_info.get('user_id') == user_id and task_info.get('url') == urls[0]:
                logger.info(f"User {user_id} already has active task for URL: {urls[0]}")
                return
        
        # Process only the first URL to avoid spam
        url = urls[0]
        
        # Filter out spam/invalid URLs
        if is_spam_url(url):
            logger.info(f"Blocking spam URL: {url}")
            try:
                await event.respond("🚫 **URL bị chặn**\n💡 Chỉ hỗ trợ URL video từ các nền tảng uy tín.")
            except Exception:
                pass  # If we can't respond, just ignore
            return
        
        # Check if URL is from a supported video platform
       
        # Check if we can access this topic/chat before processing
        if not await self.is_topic_accessible(event):
            logger.info(f"Skipping URL in inaccessible topic/chat: {url}")
            return
        
        try:
            await self.process_video_url(event, url)
        except Exception as e:
            # Log the error but don't crash the handler
            logger.error(f"Error processing URL in handle_message: {url}, error: {e}")
            
            # Don't try to respond if it's a TOPIC_CLOSED error
            if "TOPIC_CLOSED" in str(e):
                logger.info(f"Cannot respond in closed topic for URL: {url}")
                return
                
            try:
                # Try to notify the user about the error
                await event.respond(f"❌ Không thể xử lý URL: {url}\nLỗi: {str(e)}")
            except Exception as respond_error:
                # If we can't even respond to the user, just log it
                logger.error(f"Failed to send error message to user: {respond_error}")
    
    async def handle_cancel(self, event):
        """Handle /cancel command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        if not self.is_authorized(event.sender_id):
            # await event.respond("❌ Bạn không có quyền sử dụng lệnh này.")
            return
            
        user_id = event.sender_id
        
        # Find and cancel tasks for this user
        user_tasks = []
        for task_id, task_info in list(self.active_tasks.items()):
            if task_info.get('user_id') == user_id:
                user_tasks.append((task_id, task_info))
        
        if not user_tasks:
            await event.respond("ℹ️ Bạn không có tác vụ nào đang chạy.")
            return
        
        # Cancel user's tasks
        cancelled_count = 0
        for task_id, task_info in user_tasks:
            try:
                task_info['task'].cancel()
                cancelled_count += 1
                logger.info(f"Cancelled task {task_id} for user {user_id}")
                
                # Update status message
                await task_info['status_msg'].edit(
                    f"❌ **Tác vụ đã bị hủy**\n🔗 URL: `{task_info['url']}`"
                )
                
                # Remove from active tasks
                del self.active_tasks[task_id]
                
            except Exception as e:
                logger.warning(f"Error cancelling task {task_id}: {e}")
        
        await event.respond(f"✅ Đã hủy {cancelled_count} tác vụ của bạn.")
    
    async def handle_forward_command(self, event):
        """Handle /forward command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return

        if not self.is_authorized(event.sender_id):
            # await event.respond("❌ Bạn không có quyền sử dụng lệnh này.")
            return
            
        # Find the most recent pending task for this user
        pending_task = self.find_pending_task(event.sender_id)
        
        if not pending_task:
            await event.respond("ℹ️ Không có video nào đang chờ xử lý. Hãy gửi URL video trước.")
            return
        
        task_id, task_info = pending_task
        await self.handle_forward_action_direct(task_id)
    
    async def handle_download_command(self, event):
        """Handle /download command"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        
        if not self.is_authorized(event.sender_id):
            # await event.respond("❌ Bạn không có quyền sử dụng lệnh này.")
            return
            
        # Find the most recent pending task for this user
        pending_task = self.find_pending_task(event.sender_id)

        
        
        if not pending_task:
            await event.respond("ℹ️ Không có video nào đang chờ xử lý. Hãy gửi URL video trước.")
            return
        
        
        
        task_id, task_info = pending_task
        await self.handle_download_action_direct(task_id, event.sender_id)
    
    def find_pending_task(self, user_id: int):
        """Find the most recent pending task for a user"""
        for task_id, task_info in self.active_tasks.items():
            if (task_info.get('stage') == 'info' and 
                task_info.get('user_id') == user_id):
                return task_id, task_info
        return None
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if a user is authorized to use restricted commands
        
        Args:
            user_id: The Telegram user ID to check
            
        Returns:
            bool: True if the user is authorized, False otherwise
        """
        return is_user_allowed(user_id)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is admin (can manage other users)
        
        Args:
            user_id: The Telegram user ID to check
            
        Returns:
            bool: True if the user is admin, False otherwise
        """
        return ADMIN_USER_ID and user_id == ADMIN_USER_ID
    
    def is_allowed_chat(self, event) -> bool:
        """Check if the chat is allowed for bot operations
        
        Args:
            event: The message event
            
        Returns:
            bool: True if chat is allowed, False otherwise
        """
        chat_id = event.chat_id
        user_id = event.sender_id
        
        # Only allow messages from:
        # 1. Target chat/group (TARGET_CHAT_ID)
        # 2. Private chat with bot (chat_id == user_id, means it's a private chat)
        is_target_chat = chat_id == TARGET_CHAT_ID
        is_private_chat = chat_id == user_id
        
        if not (is_target_chat or is_private_chat):
            return False
            
        return True
    
    async def is_topic_accessible(self, event) -> bool:
        """Check if the current topic/chat is accessible for bot operations
        
        Args:
            event: The message event
            
        Returns:
            bool: True if accessible, False if closed topic or other access issues
        """
        try:
            # Try to get basic chat info
            chat = await event.get_chat()
            
            # For forum chats, we might need additional checks
            if hasattr(chat, 'forum') and chat.forum:
                # This is a forum - topic might be closed
                # The actual check will happen when we try to respond
                pass
                
            return True
        except Exception as e:
            if "TOPIC_CLOSED" in str(e):
                return False
            # For other errors, assume accessible (will be caught later)
            return True
    
    async def process_video_url(self, event, url: str):
        """Process video URL"""
        # Create task ID
        self.task_counter += 1
        task_id = str(self.task_counter)
        
        # Initialize status_msg to None before the try block
        status_msg = None
        
        try:
            # Send processing message
            try:
                status_msg = await event.respond(
                    f"🔄 **Đang xử lý URL:**\n`{url}`\n⏳ Đang lấy thông tin video..."
                )
            except Exception as respond_error:
                # Check for TOPIC_CLOSED error specifically
                if "TOPIC_CLOSED" in str(respond_error):
                    logger.info(f"Cannot respond in closed topic, skipping URL: {url}")
                    # We can't respond in this topic, so just return
                    return
                else:
                    # Re-raise other errors
                    raise
            
            # Create and store task
            main_task = asyncio.create_task(self._process_video_task(status_msg, url, task_id))
            self.active_tasks[task_id] = {
                'task': main_task,
                'url': url,
                'status_msg': status_msg,
                'stage': 'info',
                'user_id': event.sender_id
            }
            
            # Don't wait for task completion here
            # Let the task run in the background
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            # Only try to edit the message if it was successfully created
            if status_msg:
                try:
                    await status_msg.edit(f"❌ Lỗi xử lý URL: {str(e)}")
                except Exception as edit_error:
                    logger.error(f"Error editing message: {edit_error}")
            else:
                # If we couldn't send the initial message, try to send a new one
                try:
                    await event.respond(f"❌ Lỗi xử lý URL: {str(e)}")
                except Exception as respond_error:
                    logger.error(f"Error sending error message: {respond_error}")
            
            # Only remove task from active_tasks if there's an error
            self.active_tasks.pop(task_id, None)
    
    async def _process_video_task(self, status_msg, url: str, task_id: str):
        """Main video processing task"""
        try:
            # Update task stage
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['stage'] = 'info'
            
            # Get video info
            video_info = self.downloader.get_video_info(url)
            
            if not video_info:
                await status_msg.edit(f"❌ Không thể lấy thông tin video từ: `{url}`")
                # Remove task if video info cannot be retrieved
                if task_id in self.active_tasks:
                    self.active_tasks.pop(task_id, None)
                return
            
            # Show video info
            platform = get_video_platform(url) or "Unknown"
            duration_str = format_duration(video_info['duration']) if video_info['duration'] else "N/A"
            size_str = format_file_size(video_info['filesize']) if video_info['filesize'] else "N/A"
            
            info_text = f"""
📹 **Thông tin video:**
🎬 **Tiêu đề:** {video_info['title'][:50]}...
👤 **Tác giả:** {video_info['uploader']}
🌐 **Nền tảng:** {platform}
⏱️ **Thời lượng:** {duration_str}
💾 **Kích thước:** {size_str}

**Gửi lệnh để chọn hành động:**
• `/forward` - Download video
• `/cancel` - Hủy bỏ tác vụ
• `/fowd_photos` - Download ảnh
            """
            
            await status_msg.edit(info_text)
            
            # Store video info in task for later use
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['video_info'] = video_info
            
            # Task stays in active_tasks, waiting for user command
            # No need to return or complete the task here
            
            # Wait indefinitely until user takes action or cancels
            while task_id in self.active_tasks and self.active_tasks[task_id]['stage'] == 'info':
                await asyncio.sleep(1)
            
        except asyncio.CancelledError:
            logger.info(f"Video task {task_id} was cancelled")
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
            raise
        except Exception as e:
            logger.error(f"Error in video task {task_id}: {e}")
            await status_msg.edit(f"❌ Lỗi xử lý video: {str(e)}")
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
    
    async def download_video_async_cancellable(self, url: str, task_id: str) -> str:
        """Download video in executor with cancellation support"""
        loop = asyncio.get_event_loop()
        
        # Create download task
        download_task = loop.run_in_executor(None, self.downloader.download_video, url)
        
        try:
            # Wait for download with cancellation check
            while not download_task.done():
                # Check if task was cancelled
                if task_id not in self.active_tasks:
                    download_task.cancel()
                    raise asyncio.CancelledError("Download cancelled by user")
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
            
            return await download_task
            
        except asyncio.CancelledError:
            # Try to cancel the download task
            download_task.cancel()
            raise
    
    async def upload_and_forward_cancellable(self, status_msg, file_path: str, url: str, video_info: dict, task_id: str):
        """Upload video to target chat using client with cancellation support"""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            await status_msg.edit(
                f"📤 **Đang chuyển tiếp video...**\n"
                f"📁 File: `{os.path.basename(file_path)}`\n"
                f"💾 Kích thước: {file_size_mb:.1f}MB\n"
                f"⏳ Vui lòng đợi..."
            )
            
            # Prepare caption
            caption = f"🎬 **Video từ:** {url}\n👤 **Tác giả:** {video_info['uploader']} \n"
            
            # Get video duration for attributes
            duration = video_info.get('duration', 0)
            
            # Get video dimensions for preserved aspect ratio
            width, height = await self.get_video_dimensions(file_path)
            
            # Upload with video attributes including dimensions
            attributes = []
            if duration > 0 and width > 0 and height > 0:
                attributes.append(DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    supports_streaming=True
                ))
            
            # Upload file with cancellation check
            upload_task = self.client.send_file(
                TARGET_CHAT_ID,
                file_path,
                caption=caption,
                attributes=attributes,
                supports_streaming=True,
                progress_callback=lambda current, total: self.upload_progress_cancellable(
                    status_msg, current, total, file_size_mb, task_id
                )
            )
            
            await upload_task
            
            # Success message
            await status_msg.edit(
                f"✅ **Hoàn thành!**\n"
                f"🎬 Video đã được chuyển tiếp thành công!\n"
                f"📁 Kích thước: {file_size_mb:.1f}MB\n"
                f"🔗 URL: `{url}`"
            )
            
            # Clean up
            self.downloader.cleanup_file(file_path)
            
        except asyncio.CancelledError:
            logger.info(f"Upload task {task_id} was cancelled")
            # Clean up on cancellation
            self.downloader.cleanup_file(file_path)
            raise
        except Exception as e:
            logger.error(f"Upload error: {e}")
            await status_msg.edit(
                f"❌ **Lỗi upload:**\n"
                f"📝 Chi tiết: {str(e)}\n"
                f"🔗 URL: `{url}`"
            )
            # Clean up on error
            self.downloader.cleanup_file(file_path)
    
    async def upload_progress_cancellable(self, status_msg, current: int, total: int, file_size_mb: float, task_id: str):
        """Update upload progress with cancellation check"""
        try:
            # Check if task was cancelled
            if task_id not in self.active_tasks:
                raise asyncio.CancelledError("Upload cancelled by user")
            
            if total > 0:
                percentage = (current / total) * 100
                await status_msg.edit(
                    f"📤 **Đang upload... {percentage:.1f}%**\n"
                    f"💾 Kích thước: {file_size_mb:.1f}MB\n"
                    f"📊 Tiến trình: {current // (1024*1024):.1f}MB / {total // (1024*1024):.1f}MB"
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            pass  # Ignore progress update errors
    
    
    async def handle_forward_action_direct(self, task_id: str):
        """Handle forward action"""
        if task_id not in self.active_tasks:
            return
        
        task_info = self.active_tasks[task_id]
        status_msg = task_info['status_msg']
        url = task_info['url']
        
        try:
            # Update task stage
            self.active_tasks[task_id]['stage'] = 'download'
            self.active_tasks[task_id]['action'] = 'forward'
            
            # Show downloading status
            await status_msg.edit(
                f"⬇️ **Đang tải video...**\n🔗 URL: `{url}`\n⏳ Vui lòng đợi..."
            )
            
            # Download video
            file_path = await self.download_video_async_cancellable(url, task_id)
            
            if not file_path:
                await status_msg.edit(
                    f"❌ **Không thể tải video!**\n"
                    f"🔗 URL: `{url}`\n"
                    f"💡 Video có thể bị giới hạn địa lý hoặc riêng tư."
                )
                # Remove task if download failed
                if task_id in self.active_tasks:
                    self.active_tasks.pop(task_id, None)
                return
            
            # Update task stage
            self.active_tasks[task_id]['stage'] = 'upload'
            
            # Get video info for upload
            video_info = self.downloader.get_video_info(url)
            
            # Upload to target chat
            await self.upload_and_forward_cancellable(status_msg, file_path, url, video_info, task_id)
            
            # Remove task after successful completion
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
            
        except asyncio.CancelledError:
            logger.info(f"Forward task {task_id} was cancelled")
            # Remove task if cancelled
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
        except Exception as e:
            logger.error(f"Error in forward action: {e}")
            await status_msg.edit(f"❌ Lỗi khi chuyển tiếp: {str(e)}")
            # Remove task if error occurred
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
    
    async def handle_download_action_direct(self, task_id: str, user_id: int):
        """Handle download to user action"""
        if task_id not in self.active_tasks:
            return
        
        task_info = self.active_tasks[task_id]
        status_msg = task_info['status_msg']
        url = task_info['url']
        
        try:
            # Update task stage
            self.active_tasks[task_id]['stage'] = 'download'
            self.active_tasks[task_id]['action'] = 'user'
            
            # Show downloading status
            await status_msg.edit(
                f"💾 **Đang tải video cho bạn...**\n🔗 URL: `{url}`\n⏳ Vui lòng đợi..."
            )
            
            # Download video
            file_path = await self.download_video_async_cancellable(url, task_id)
            
            if not file_path:
                await status_msg.edit(
                    f"❌ **Không thể tải video!**\n"
                    f"🔗 URL: `{url}`\n"
                    f"💡 Video có thể bị giới hạn địa lý hoặc riêng tư."
                )
                # Remove task if download failed
                if task_id in self.active_tasks:
                    self.active_tasks.pop(task_id, None)
                return
            
            # Update task stage
            self.active_tasks[task_id]['stage'] = 'upload'
            
            # Send video to user
            await self.send_video_to_user(status_msg, file_path, url, user_id, task_id)
            
            # Remove task after successful completion
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
            
        except asyncio.CancelledError:
            logger.info(f"Download task {task_id} was cancelled")
            # Clean up temp file if exists
            if 'file_path' in locals() and file_path:
                self.downloader.cleanup_file(file_path)
            # Remove task if cancelled
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
        except Exception as e:
            logger.error(f"Error in download action: {e}")
            await status_msg.edit(f"❌ Lỗi khi tải video: {str(e)}")
            # Remove task if error occurred
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
    
    async def send_video_to_user(self, status_msg, file_path: str, url: str, user_id: int, task_id: str):
        """Send video directly to user with preserved aspect ratio"""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            await status_msg.edit(
                f"📤 **Đang gửi video cho bạn...**\n"
                f"📁 File: `{os.path.basename(file_path)}`\n"
                f"💾 Kích thước: {file_size_mb:.1f}MB\n"
                f"⏳ Vui lòng đợi..."
            )
            
            # Get video info for metadata
            video_info = self.downloader.get_video_info(url)
            
            # Prepare caption
            caption = f"🎬 **Video đã tải:**\n📹 {video_info['title'][:100]}...\n👤 {video_info['uploader']}\n🔗 {url}"
            
            # Get video dimensions and duration for attributes
            duration = video_info.get('duration', 0)
            width, height = await self.get_video_dimensions(file_path)
            
            # Create video attributes with preserved aspect ratio
            attributes = []
            if duration > 0 and width > 0 and height > 0:
                attributes.append(DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    supports_streaming=True
                ))
            
            # Send video to user with cancellation check
            upload_task = self.client.send_file(
                user_id,
                file_path,
                caption=caption,
                attributes=attributes,
                supports_streaming=True,
                progress_callback=lambda current, total: self.upload_progress_cancellable(
                    status_msg, current, total, file_size_mb, task_id
                )
            )
            
            await upload_task
            
            # Success message
            await status_msg.edit(
                f"✅ **Video đã gửi thành công!**\n"
                f"🎬 Video đã được gửi vào chat riêng của bạn\n"
                f"📁 Kích thước: {file_size_mb:.1f}MB\n"
                f"🔗 URL: `{url}`"
            )
            
            # Clean up
            self.downloader.cleanup_file(file_path)
            
        except asyncio.CancelledError:
            logger.info(f"User upload task {task_id} was cancelled")
            # Clean up on cancellation
            self.downloader.cleanup_file(file_path)
            raise
        except Exception as e:
            logger.error(f"User upload error: {e}")
            await status_msg.edit(
                f"❌ **Lỗi gửi video:**\n"
                f"📝 Chi tiết: {str(e)}\n"
                f"🔗 URL: `{url}`"
            )
            # Clean up on error
            self.downloader.cleanup_file(file_path)

    async def handle_photos_command(self, event):
        """Handle /photos command: send images from TikTok slideshow instead of video"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        if not self.is_authorized(event.sender_id):
            return

        pending_task = self.find_pending_task(event.sender_id)
        if not pending_task:
            await event.respond("ℹ️ Không có URL nào đang chờ xử lý. Hãy gửi URL TikTok photo trước.")
            return

        task_id, task_info = pending_task
        status_msg = task_info['status_msg']
        url = task_info['url']

        # Only applicable for TikTok photo URLs
        if 'tiktok.com' not in url or ('/photo/' not in url and 'slideshow' not in url.lower()):
            await status_msg.edit("ℹ️ Lệnh `/photos` chỉ áp dụng cho TikTok Photo Slideshow.")
            return

        try:
            self.active_tasks[task_id]['stage'] = 'download'
            self.active_tasks[task_id]['action'] = 'photos'
            await status_msg.edit("⬇️ **Đang tải bộ ảnh slideshow...**\n⏳ Vui lòng đợi...")

            loop = asyncio.get_event_loop()
            image_paths = await loop.run_in_executor(None, self.downloader.download_tiktok_images, url)
            if not image_paths:
                await status_msg.edit("❌ Không tìm thấy ảnh trong slideshow hoặc tải thất bại.")
                if task_id in self.active_tasks:
                    self.active_tasks.pop(task_id, None)
                return

            await status_msg.edit(f"📤 **Đang gửi {len(image_paths)} ảnh...**")

            # Send images as media groups (max 10 per album message)
            CHUNK_SIZE = 10
            total = len(image_paths)
            for i in range(0, total, CHUNK_SIZE):
                if task_id not in self.active_tasks:
                    raise asyncio.CancelledError("Photos sending cancelled by user")
                chunk = image_paths[i:i + CHUNK_SIZE]
                await status_msg.edit(f"📤 **Đang gửi ảnh...** {min(i + CHUNK_SIZE, total)}/{total}")
                await self.client.send_file(
                    event.sender_id,
                    chunk,
                    caption=("📸 Ảnh nè" if i == 0 else None),
                    part_size_kb=512,
                    force_document=False
                )

            await status_msg.edit(f"✅ **Đã gửi xong {total} ảnh!**")

        except asyncio.CancelledError:
            if 'image_paths' in locals() and image_paths:
                self.downloader.cleanup_files(image_paths)
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
            raise
        except Exception as e:
            logger.error(f"Error sending photos: {e}")
            await status_msg.edit(f"❌ Lỗi khi gửi ảnh: {str(e)}")
        finally:
            if 'image_paths' in locals() and image_paths:
                self.downloader.cleanup_files(image_paths)
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)

    async def handle_photos_forward_command(self, event):
        """Handle /photos_forward command: send images to target group"""
        # Check if command is from allowed chat
        if not self.is_allowed_chat(event):
            return
        if not self.is_authorized(event.sender_id):
            return
        
        pending_task = self.find_pending_task(event.sender_id)
        if not pending_task:
            await event.respond("ℹ️ Không có URL nào đang chờ xử lý. Hãy gửi URL TikTok photo trước.")
            return

        task_id, task_info = pending_task
        status_msg = task_info['status_msg']
        url = task_info['url']

        # Only applicable for TikTok photo URLs
        if 'tiktok.com' not in url or ('/photo/' not in url and 'slideshow' not in url.lower()):
            await status_msg.edit("ℹ️ Lệnh `/photos_forward` chỉ áp dụng cho TikTok Photo Slideshow.")
            return

        try:
            self.active_tasks[task_id]['stage'] = 'download'
            self.active_tasks[task_id]['action'] = 'photos_forward'
            await status_msg.edit("⬇️ **Đang tải bộ ảnh slideshow để gửi vào nhóm...**\n⏳ Vui lòng đợi...")

            loop = asyncio.get_event_loop()
            image_paths = await loop.run_in_executor(None, self.downloader.download_tiktok_images, url)
            if not image_paths:
                await status_msg.edit("❌ Không tìm thấy ảnh trong slideshow hoặc tải thất bại.")
                if task_id in self.active_tasks:
                    self.active_tasks.pop(task_id, None)
                return

            await status_msg.edit(f"📤 **Đang gửi {len(image_paths)} ảnh vào nhóm...**")

            # Send images as media groups (max 10 per album message)
            CHUNK_SIZE = 10
            total = len(image_paths)
            for i in range(0, total, CHUNK_SIZE):
                if task_id not in self.active_tasks:
                    raise asyncio.CancelledError("Photos sending cancelled by user")
                chunk = image_paths[i:i + CHUNK_SIZE]
                await status_msg.edit(f"📤 **Đang gửi ảnh vào nhóm...** {min(i + CHUNK_SIZE, total)}/{total}")
                await self.client.send_file(
                    TARGET_CHAT_ID,
                    chunk,
                    caption=("📸 Ảnh nè" if i == 0 else None),
                    part_size_kb=512,
                    force_document=False
                )

            await status_msg.edit(f"✅ **Đã gửi xong {total} ảnh vào nhóm!**")

        except asyncio.CancelledError:
            if 'image_paths' in locals() and image_paths:
                self.downloader.cleanup_files(image_paths)
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
            raise
        except Exception as e:
            logger.error(f"Error sending photos to group: {e}")
            await status_msg.edit(f"❌ Lỗi khi gửi ảnh vào nhóm: {str(e)}")
        finally:
            if 'image_paths' in locals() and image_paths:
                self.downloader.cleanup_files(image_paths)
            if task_id in self.active_tasks:
                self.active_tasks.pop(task_id, None)
    
    async def get_video_dimensions(self, file_path: str) -> tuple:
        """Get video dimensions using ffprobe"""
        try:
            import subprocess
            import json
            
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Find video stream
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        width = stream.get('width', 0)
                        height = stream.get('height', 0)
                        if width > 0 and height > 0:
                            return width, height
            
            # Fallback dimensions
            return 1280, 720
            
        except Exception as e:
            logger.warning(f"Could not get video dimensions: {e}")
            return 1280, 720  # Default HD dimensions
    
    async def run(self):
        """Run the client"""
        await self.start()
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await self.client.run_until_disconnected()

async def main():
    """Main function"""
    bot = TelegramVideoClient()
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())