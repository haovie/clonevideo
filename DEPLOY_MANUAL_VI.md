# 🔧 HƯỚNG DẪN DEPLOY THỦ CÔNG LÊN DIGITAL OCEAN

## 📋 Tổng quan

Chúng ta sẽ:
1. Chuẩn bị Droplet (cài Docker)
2. Copy code lên server
3. Build và chạy bot
4. Setup auto-start

---

## BƯỚC 1: SSH VÀO DROPLET

### 1.1 Kết nối SSH

```bash
ssh root@YOUR_DROPLET_IP
```

**Giải thích:**
- `root` - user mặc định của Digital Ocean
- `YOUR_DROPLET_IP` - IP của droplet (ví dụ: 104.248.123.45)
- Lần đầu sẽ hỏi "Are you sure...?" → gõ `yes`
- Nhập password (hoặc dùng SSH key)

### 1.2 Kiểm tra hệ thống

```bash
# Xem phiên bản Ubuntu
cat /etc/os-release

# Xem dung lượng disk
df -h

# Xem RAM
free -h
```

**Giải thích:**
- Nên dùng Ubuntu 20.04 hoặc 22.04
- Cần ít nhất 1GB RAM, 5GB disk free

---

## BƯỚC 2: CÀI ĐẶT DOCKER

### 2.1 Update hệ thống

```bash
apt update
apt upgrade -y
```

**Giải thích:**
- `apt update` - Cập nhật danh sách package
- `apt upgrade -y` - Upgrade tất cả package (-y = yes tự động)
- Có thể mất 2-5 phút

### 2.2 Cài Docker

```bash
# Download script cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh

# Xem script (optional - để kiểm tra)
cat get-docker.sh

# Chạy script
sh get-docker.sh

# Xóa script
rm get-docker.sh
```

**Giải thích:**
- `curl -fsSL` - Download file từ URL
- `https://get.docker.com` - Script official của Docker
- `sh get-docker.sh` - Chạy script cài đặt
- Mất khoảng 1-2 phút

### 2.3 Start Docker service

```bash
# Enable Docker tự chạy khi boot
systemctl enable docker

# Start Docker ngay
systemctl start docker

# Kiểm tra status
systemctl status docker
```

**Giải thích:**
- `systemctl` - Quản lý services trên Linux
- `enable` - Tự chạy khi khởi động server
- `start` - Chạy ngay bây giờ
- `status` - Xem trạng thái (nhấn `q` để thoát)

### 2.4 Test Docker

```bash
docker --version
docker ps
```

**Giải thích:**
- `docker --version` - Xem phiên bản Docker
- `docker ps` - Xem các container đang chạy (hiện tại = rỗng)

### 2.5 Cài Docker Compose

```bash
# Download Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Chmod để chạy được
chmod +x /usr/local/bin/docker-compose

# Test
docker-compose --version
```

**Giải thích:**
- `$(uname -s)` - Tên OS (Linux)
- `$(uname -m)` - Kiến trúc (x86_64)
- `-o /usr/local/bin/docker-compose` - Lưu vào folder bin
- `chmod +x` - Thêm quyền executable

---

## BƯỚC 3: TẠO THỦ MỤC PROJECT

### 3.1 Tạo folder

```bash
# Tạo thư mục
mkdir -p /opt/telegram-bot

# Vào thư mục
cd /opt/telegram-bot

# Kiểm tra vị trí hiện tại
pwd
```

**Giải thích:**
- `/opt/` - Thư mục chuẩn cho applications
- `mkdir -p` - Tạo folder (p = parent directories)
- `pwd` - Print Working Directory (xem đang ở đâu)

### 3.2 Tạo các folder con

```bash
# Tạo folder cho session và downloads
mkdir -p session_data downloads

# Set permissions
chmod 755 session_data downloads

# Kiểm tra
ls -la
```

**Giải thích:**
- `session_data` - Lưu file session của Telegram
- `downloads` - Lưu video tải về (tạm thời)
- `chmod 755` - Owner: full, others: read+execute
- `ls -la` - List files chi tiết

---

## BƯỚC 4: COPY CODE LÊN SERVER

**Có 3 cách, chọn 1:**

### Cách 1: Dùng rsync (Khuyến nghị)

**Trên máy LOCAL** (mở terminal mới):

```bash
# Vào thư mục project
cd ~/path/to/your/telegram-bot

# Copy files lên server
rsync -avz --progress \
    --exclude='session_data/' \
    --exclude='downloads/' \
    --exclude='env-download-bot/' \
    --exclude='web-app/' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='*.session' \
    --exclude='.git' \
    ./ root@YOUR_DROPLET_IP:/opt/telegram-bot/
```

**Giải thích:**
- `rsync` - Tool sync files (tốt hơn cp/scp)
- `-a` - Archive mode (giữ permissions)
- `-v` - Verbose (hiện chi tiết)
- `-z` - Compress (nén khi transfer)
- `--progress` - Hiện tiến trình
- `--exclude` - Bỏ qua các folder/file không cần
- `./` - Từ folder hiện tại
- `root@IP:/path` - Đến server

### Cách 2: Dùng git (Nếu code ở GitHub)

**Trên DROPLET:**

```bash
cd /opt/telegram-bot

# Clone repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# (Dấu . ở cuối = clone vào folder hiện tại)
```

**Giải thích:**
- Cần push code lên GitHub trước
- Clone về server
- Dễ update sau này (git pull)

### Cách 3: Dùng scp (Đơn giản nhất)

**Trên máy LOCAL:**

```bash
cd ~/path/to/your/telegram-bot

# Copy từng file
scp client_bot.py root@YOUR_IP:/opt/telegram-bot/
scp downloader.py root@YOUR_IP:/opt/telegram-bot/
scp config.py root@YOUR_IP:/opt/telegram-bot/
scp utils.py root@YOUR_IP:/opt/telegram-bot/
scp audio_enhancer.py root@YOUR_IP:/opt/telegram-bot/
scp run.py root@YOUR_IP:/opt/telegram-bot/
scp requirements.txt root@YOUR_IP:/opt/telegram-bot/
scp Dockerfile root@YOUR_IP:/opt/telegram-bot/
scp docker-compose.yml root@YOUR_IP:/opt/telegram-bot/
scp .dockerignore root@YOUR_IP:/opt/telegram-bot/
scp allowed_users.json root@YOUR_IP:/opt/telegram-bot/
```

**Giải thích:**
- `scp` - Secure Copy
- Copy từng file một
- Cách này lâu nhưng đơn giản

---

## BƯỚC 5: TẠO FILE .ENV TRÊN SERVER

### 5.1 Tạo file .env

**Trên DROPLET:**

```bash
cd /opt/telegram-bot

# Tạo file .env
nano .env
```

**Giải thích:**
- `nano` - Text editor đơn giản trên Linux
- Sẽ mở editor

### 5.2 Paste nội dung

Paste vào (Ctrl+Shift+V hoặc chuột phải):

```env
# Telegram API credentials
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+84xxxxxxxxx
TARGET_CHAT_ID=-100xxxxxxxxx
ADMIN_USER_ID=your_user_id

# Optional
ALLOWED_USERS_STR=
DOWNLOAD_DIR=./downloads
```

**Thay thế:**
- `your_api_id` - API ID từ my.telegram.org/apps
- `your_api_hash` - API Hash từ my.telegram.org/apps
- `+84xxxxxxxxx` - Số điện thoại của bạn
- `-100xxxxxxxxx` - Chat ID đích
- `your_user_id` - User ID của bạn

### 5.3 Lưu file

```
Ctrl + O   (save)
Enter      (confirm)
Ctrl + X   (exit)
```

### 5.4 Kiểm tra

```bash
# Xem nội dung (đảm bảo đã lưu)
cat .env

# Hoặc
ls -la .env
```

**Giải thích:**
- `cat .env` - Hiện nội dung file
- `ls -la .env` - Xem thông tin file

---

## BƯỚC 6: KIỂM TRA FILES

```bash
cd /opt/telegram-bot

# Xem tất cả files
ls -la

# Kiểm tra các file quan trọng
ls -l client_bot.py downloader.py config.py run.py Dockerfile docker-compose.yml .env
```

**Phải có:**
- ✅ client_bot.py
- ✅ downloader.py
- ✅ config.py
- ✅ utils.py
- ✅ audio_enhancer.py
- ✅ run.py
- ✅ requirements.txt
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ .dockerignore
- ✅ .env
- ✅ allowed_users.json
- ✅ session_data/ (folder)
- ✅ downloads/ (folder)

---

## BƯỚC 7: BUILD DOCKER IMAGE

### 7.1 Build image

```bash
cd /opt/telegram-bot

# Build
docker-compose build
```

**Giải thích:**
- `docker-compose build` - Build Docker image theo Dockerfile
- Mất khoảng 2-5 phút lần đầu
- Sẽ tải Python, cài packages (telethon, yt-dlp, etc.)

**Quá trình:**
1. Tải base image (Python 3.11-slim)
2. Cài ffmpeg
3. Cài Python packages từ requirements.txt
4. Copy code vào image

### 7.2 Xem images

```bash
docker images
```

**Giải thích:**
- Sẽ thấy image `download-video-from-url-telegram-bot`
- Size khoảng 450-500MB

---

## BƯỚC 8: CHẠY BOT

### 8.1 Start container

```bash
cd /opt/telegram-bot

# Start
docker-compose up -d
```

**Giải thích:**
- `docker-compose up` - Chạy services trong docker-compose.yml
- `-d` - Detached mode (chạy background)
- Không có `-d` = chạy foreground (sẽ thấy logs)

### 8.2 Xem logs

```bash
# Xem logs real-time
docker-compose logs -f

# Hoặc
docker logs telegram-video-bot -f
```

**Giải thích:**
- `-f` - Follow (real-time, như tail -f)
- Nhấn `Ctrl+C` để thoát (bot vẫn chạy)

**Nếu lần đầu (chưa có session):**
- Bot sẽ gửi code qua Telegram
- Nhập code vào (trong logs hoặc chat với bot)
- Session được lưu vào `session_data/`

**Nếu thành công, sẽ thấy:**
```
Client started successfully!
Event handlers registered. Bot is ready!
```

### 8.3 Kiểm tra status

```bash
# Xem container đang chạy
docker-compose ps

# Hoặc
docker ps
```

**Giải thích:**
- Sẽ thấy `telegram-video-bot` với status `Up`

---

## BƯỚC 9: TEST BOT

### 9.1 Gửi video URL

- Mở Telegram
- Gửi URL video vào chat đích (TARGET_CHAT_ID)
- Hoặc chat riêng với số điện thoại bot

### 9.2 Xem logs

```bash
docker-compose logs -f
```

**Sẽ thấy:**
- Bot nhận URL
- Tải video
- Upload lên Telegram

---

## BƯỚC 10: SETUP AUTO-START (Quan trọng!)

**Mục đích:** Bot tự chạy khi server reboot

### 10.1 Tạo systemd service

```bash
nano /etc/systemd/system/telegram-bot.service
```

### 10.2 Paste config

```ini
[Unit]
Description=Telegram Video Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/telegram-bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**Giải thích:**
- `[Unit]` - Thông tin service
- `Requires=docker.service` - Cần Docker chạy trước
- `After=docker.service` - Chạy sau khi Docker start
- `[Service]` - Cấu hình service
- `WorkingDirectory` - Thư mục làm việc
- `ExecStart` - Lệnh start
- `ExecStop` - Lệnh stop
- `[Install]` - Cài đặt service

### 10.3 Lưu file

```
Ctrl + O
Enter
Ctrl + X
```

### 10.4 Enable service

```bash
# Reload systemd
systemctl daemon-reload

# Enable (tự chạy khi boot)
systemctl enable telegram-bot

# Start ngay
systemctl start telegram-bot

# Xem status
systemctl status telegram-bot
```

**Giải thích:**
- `daemon-reload` - Load config mới
- `enable` - Enable auto-start
- `start` - Start ngay
- `status` - Xem trạng thái

### 10.5 Test auto-start

```bash
# Reboot server
reboot

# Đợi 1-2 phút, SSH lại
ssh root@YOUR_DROPLET_IP

# Kiểm tra bot
systemctl status telegram-bot
docker-compose ps
```

---

## BƯỚC 11: QUẢN LÝ BOT

### Xem logs

```bash
cd /opt/telegram-bot

# Real-time logs
docker-compose logs -f

# 100 dòng cuối
docker-compose logs --tail=100

# Logs từ 10 phút trước
docker-compose logs --since 10m
```

### Restart bot

```bash
cd /opt/telegram-bot

# Cách 1: Docker Compose
docker-compose restart

# Cách 2: Systemd
systemctl restart telegram-bot

# Cách 3: Down -> Up
docker-compose down
docker-compose up -d
```

### Stop bot

```bash
cd /opt/telegram-bot

# Cách 1
docker-compose down

# Cách 2
systemctl stop telegram-bot
```

### Update code

```bash
cd /opt/telegram-bot

# Stop bot
docker-compose down

# Copy code mới (từ local hoặc git pull)
# Nếu dùng rsync: chạy lại lệnh rsync từ local
# Nếu dùng git: git pull

# Rebuild
docker-compose build

# Start
docker-compose up -d

# Xem logs
docker-compose logs -f
```

---

## BƯỚC 12: BACKUP SESSION (Rất quan trọng!)

### 12.1 Backup thủ công

```bash
cd /opt/telegram-bot

# Tạo backup
tar -czf ~/telegram-bot-backup-$(date +%Y%m%d).tar.gz \
    session_data/ \
    allowed_users.json \
    .env

# Xem backup
ls -lh ~/*.tar.gz
```

### 12.2 Download về local

**Trên máy LOCAL:**

```bash
# Download backup từ server
scp root@YOUR_DROPLET_IP:~/telegram-bot-backup-*.tar.gz ./

# Giải nén (nếu cần restore)
tar -xzf telegram-bot-backup-YYYYMMDD.tar.gz
```

### 12.3 Setup auto backup (optional)

```bash
# Tạo backup script
nano /opt/telegram-bot/backup.sh
```

Paste:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/telegram-bot_$DATE.tar.gz \
    -C /opt/telegram-bot \
    session_data/ \
    allowed_users.json \
    .env

# Keep last 7 backups
ls -t $BACKUP_DIR/telegram-bot_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup created: telegram-bot_$DATE.tar.gz"
```

```bash
# Chmod
chmod +x /opt/telegram-bot/backup.sh

# Test
/opt/telegram-bot/backup.sh

# Setup cronjob (backup mỗi ngày lúc 2am)
crontab -e
# Thêm dòng:
0 2 * * * /opt/telegram-bot/backup.sh
```

---

## BƯỚC 13: MONITORING

### Xem resource usage

```bash
# Container stats
docker stats telegram-video-bot

# Disk usage
df -h
du -sh /opt/telegram-bot/downloads/

# Memory
free -h

# Top processes
htop  # (nếu chưa có: apt install htop)
```

### Clean downloads

```bash
# Xóa downloads cũ
cd /opt/telegram-bot
rm -rf downloads/*

# Hoặc setup cronjob (mỗi ngày lúc 3am)
crontab -e
# Thêm:
0 3 * * * rm -rf /opt/telegram-bot/downloads/*
```

### Clean Docker

```bash
# Xem disk usage của Docker
docker system df

# Clean up (cẩn thận!)
docker system prune -a
```

---

## BƯỚC 14: SECURITY (Khuyến nghị)

### 14.1 Setup Firewall

```bash
# Allow SSH
ufw allow 22/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 14.2 Secure SSH

```bash
nano /etc/ssh/sshd_config
```

Tìm và sửa:
```
PermitRootLogin no           # Disable root login
PasswordAuthentication no    # Chỉ dùng SSH key
```

Restart SSH:
```bash
systemctl restart sshd
```

### 14.3 Tạo user thường (không dùng root)

```bash
# Tạo user mới
adduser botadmin

# Add vào group docker
usermod -aG docker botadmin
usermod -aG sudo botadmin

# Copy SSH key
mkdir -p /home/botadmin/.ssh
cp ~/.ssh/authorized_keys /home/botadmin/.ssh/
chown -R botadmin:botadmin /home/botadmin/.ssh
chmod 700 /home/botadmin/.ssh
chmod 600 /home/botadmin/.ssh/authorized_keys

# Test login
# ssh botadmin@YOUR_DROPLET_IP
```

---

## ✅ HOÀN TẤT!

Bot đã chạy trên Digital Ocean Droplet!

### Checklist:
- [ ] Docker đã cài
- [ ] Code đã copy lên
- [ ] .env đã tạo
- [ ] Build thành công
- [ ] Bot đang chạy
- [ ] Đã test với video URL
- [ ] Setup auto-start
- [ ] Backup session

### Commands thường dùng:

```bash
# SSH
ssh root@YOUR_IP

# Vào project
cd /opt/telegram-bot

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Status
systemctl status telegram-bot
docker-compose ps

# Backup
tar -czf ~/backup.tar.gz session_data/ allowed_users.json .env
```

---

**Bot đang chạy trên cloud! ☁️🚀**
