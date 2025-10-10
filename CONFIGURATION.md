# Cấu hình Bot

## Giới hạn chat xử lý tin nhắn

Bot hiện tại đã được cập nhật để chỉ xử lý tin nhắn từ:

1. **Nhóm đích (TARGET_CHAT_ID)**: Nhóm/kênh cụ thể mà bạn muốn bot hoạt động
2. **Chat riêng với bot**: Tin nhắn trực tiếp gửi cho bot

## Cấu hình trong file .env

```bash
# ID của nhóm đích
TARGET_CHAT_ID=-1001234567890

# API của Telegram
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+84xxxxxxxxx

# Bot token (nếu sử dụng)
BOT_TOKEN=your_bot_token

# User được phép dùng lệnh (legacy, tùy chọn)
ALLOWED_USERS_STR=123456789

# Admin user ID (quan trọng - có thể quản lý users khác)
ADMIN_USER_ID=987654321
```

## Cách lấy TARGET_CHAT_ID

1. **Đối với nhóm/kênh**:

   - Thêm bot @userinfobot vào nhóm
   - Gõ `/start` trong nhóm
   - Bot sẽ trả về ID của nhóm (có dạng -100xxxxxxxxx)
2. **Đối với chat riêng**:

   - Gửi `/get_user_id` cho bot để lấy User ID của bạn

## Quản lý Users (Mới)

Bot hiện hỗ trợ 2 cách quản lý users:

### 1. Qua Environment Variables (.env)
```bash
# Admin có thể quản lý users khác
ADMIN_USER_ID=987654321

# Users được phép (tùy chọn, cho compatibility)
ALLOWED_USERS_STR=123456789
```

### 2. Qua Commands (Linh hoạt)
Admin có thể sử dụng các lệnh sau:

- `/add_user <user_id>` - Thêm user mới
- `/remove_user <user_id>` - Xóa user
- `/list_users` - Xem danh sách users

**Ví dụ:**
```
/add_user 123456789
/remove_user 123456789
/list_users
```

### Ưu tiên xác thực:
1. ADMIN_USER_ID (luôn được phép)
2. ALLOWED_USERS_STR (từ .env)
3. Users trong file `allowed_users.json` (được thêm qua lệnh)

## Hoạt động của bot

- ✅ **Xử lý**: Tin nhắn trong nhóm TARGET_CHAT_ID hoặc chat riêng
- ❌ **Bỏ qua**: Tin nhắn từ các nhóm/chat khác
- 📝 **Log**: Bot sẽ ghi log khi bỏ qua tin nhắn từ chat không được phép

## Kiểm tra

Sau khi cấu hình:

1. Gửi URL video trong nhóm đích → Bot sẽ xử lý ✅
2. Gửi URL video trong chat riêng với bot → Bot sẽ xử lý ✅
3. Gửi URL video trong nhóm khác → Bot sẽ bỏ qua ❌
