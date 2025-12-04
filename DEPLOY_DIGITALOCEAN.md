# 🚀 Deploy to Digital Ocean Droplet

## Yêu cầu

- ✅ Digital Ocean Droplet (Ubuntu 20.04/22.04 recommended)
- ✅ SSH access to droplet
- ✅ `.env` file đã cấu hình

## Bước 1: Chuẩn bị Local

### 1.1 Đảm bảo có file .env

```bash
# Copy template
cp .env.example .env

# Chỉnh sửa
nano .env
```

Điền đầy đủ:
```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+84xxxxxxxxx
TARGET_CHAT_ID=-100xxxxxxxxx
ADMIN_USER_ID=your_user_id
```

### 1.2 Test local trước (optional)

```bash
docker-compose up -d
docker-compose logs -f
# Nếu OK thì stop: docker-compose down
```

## Bước 2: Deploy lên Droplet

### Method 1: Dùng script tự động (Khuyến nghị)

```bash
# Syntax
./deploy_to_droplet.sh <DROPLET_IP> [USER]

# Example
./deploy_to_droplet.sh 104.248.123.45
# hoặc với user khác
./deploy_to_droplet.sh 104.248.123.45 ubuntu
```

Script sẽ tự động:
- ✅ Cài Docker & Docker Compose (nếu chưa có)
- ✅ Copy files lên server
- ✅ Build Docker image
- ✅ Start bot

### Method 2: Deploy thủ công

#### 2.1 SSH vào Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

#### 2.2 Cài Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

#### 2.3 Tạo thư mục project

```bash
mkdir -p /opt/telegram-bot
cd /opt/telegram-bot
```

#### 2.4 Copy files từ local (chạy trên máy local)

```bash
# Copy tất cả files
rsync -avz --progress \
    --exclude='session_data/' \
    --exclude='downloads/' \
    --exclude='env-download-bot/' \
    --exclude='web-app/' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='*.md' \
    --exclude='.git' \
    ./ root@YOUR_DROPLET_IP:/opt/telegram-bot/
```

Hoặc dùng git:
```bash
# Trên droplet
git clone YOUR_REPO_URL /opt/telegram-bot
cd /opt/telegram-bot
```

#### 2.5 Tạo .env file trên server

```bash
# Trên droplet
cd /opt/telegram-bot
nano .env
```

Paste nội dung .env của bạn.

#### 2.6 Setup directories

```bash
mkdir -p session_data downloads
chmod 755 session_data downloads
```

#### 2.7 Build và chạy

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Bước 3: Xác thực lần đầu

### 3.1 Xem logs để lấy code

```bash
docker-compose logs -f
```

### 3.2 Nhập code từ Telegram

Bot sẽ gửi code qua Telegram, nhập code vào khi được hỏi.

## Bước 4: Setup Auto-start on Boot

### 4.1 Tạo systemd service

```bash
nano /etc/systemd/system/telegram-bot.service
```

Paste:
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

### 4.2 Enable service

```bash
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot
```

### 4.3 Check status

```bash
systemctl status telegram-bot
```

## Bước 5: Quản lý Bot

### Xem logs

```bash
cd /opt/telegram-bot
docker-compose logs -f

# Hoặc
docker logs telegram-video-bot -f
```

### Restart bot

```bash
cd /opt/telegram-bot
docker-compose restart

# Hoặc với systemd
systemctl restart telegram-bot
```

### Stop bot

```bash
cd /opt/telegram-bot
docker-compose down

# Hoặc
systemctl stop telegram-bot
```

### Update bot

```bash
cd /opt/telegram-bot

# Stop
docker-compose down

# Pull new code (nếu dùng git)
git pull

# Hoặc rsync từ local
# rsync -avz ./ root@YOUR_IP:/opt/telegram-bot/

# Rebuild và start
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Bước 6: Monitoring

### Check container status

```bash
docker-compose ps
docker stats telegram-video-bot
```

### Check disk usage

```bash
df -h
du -sh /opt/telegram-bot/downloads/
```

### Setup log rotation

Docker đã tự động log rotation (cấu hình trong docker-compose.yml):
- Max size: 10MB
- Max files: 3

### Clean up old downloads

```bash
# Tạo cronjob
crontab -e

# Thêm dòng này (clean mỗi ngày lúc 3am)
0 3 * * * rm -rf /opt/telegram-bot/downloads/*
```

## Bước 7: Security

### 7.1 Setup Firewall

```bash
# Allow SSH
ufw allow 22/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 7.2 Disable root login (recommended)

```bash
# Create user
adduser telegrambot
usermod -aG docker telegrambot
usermod -aG sudo telegrambot

# Copy SSH key
mkdir -p /home/telegrambot/.ssh
cp ~/.ssh/authorized_keys /home/telegrambot/.ssh/
chown -R telegrambot:telegrambot /home/telegrambot/.ssh
chmod 700 /home/telegrambot/.ssh
chmod 600 /home/telegrambot/.ssh/authorized_keys

# Disable root login
nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Restart SSH
systemctl restart sshd
```

### 7.3 Backup session

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

# Keep only last 7 backups
ls -t $BACKUP_DIR/telegram-bot_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup created: $BACKUP_DIR/telegram-bot_$DATE.tar.gz"
```

```bash
chmod +x /opt/telegram-bot/backup.sh

# Setup cronjob (backup mỗi ngày)
crontab -e
# Add: 0 2 * * * /opt/telegram-bot/backup.sh
```

## Troubleshooting

### Bot không start

```bash
# Check logs
docker-compose logs

# Check Docker service
systemctl status docker

# Restart Docker
systemctl restart docker
```

### Out of disk space

```bash
# Check disk
df -h

# Clean downloads
rm -rf /opt/telegram-bot/downloads/*

# Clean Docker
docker system prune -a
```

### Session expired

```bash
cd /opt/telegram-bot
docker-compose down
rm -rf session_data/*
docker-compose up -d
docker-compose logs -f
# Re-authenticate
```

### High memory usage

```bash
# Check stats
docker stats

# Restart bot
docker-compose restart
```

## Useful Commands Cheat Sheet

```bash
# SSH to droplet
ssh root@YOUR_IP

# Go to project
cd /opt/telegram-bot

# Logs
docker-compose logs -f
docker-compose logs --tail=100

# Status
docker-compose ps
systemctl status telegram-bot

# Restart
docker-compose restart
systemctl restart telegram-bot

# Stop
docker-compose down
systemctl stop telegram-bot

# Update
git pull && docker-compose up -d --build

# Backup
./backup.sh

# Clean
rm -rf downloads/*
docker system prune -a

# Resource usage
docker stats
htop
```

## Quick Deploy Script

Tạo file `quick_update.sh`:

```bash
#!/bin/bash
cd /opt/telegram-bot
docker-compose down
git pull
docker-compose build
docker-compose up -d
docker-compose logs -f
```

```bash
chmod +x quick_update.sh
```

## Support

Nếu gặp vấn đề:
1. Check logs: `docker-compose logs -f`
2. Check status: `docker-compose ps`
3. Check disk: `df -h`
4. Check memory: `free -h`
5. Restart: `docker-compose restart`

---

**Deployment hoàn tất! Bot của bạn đang chạy trên cloud! ☁️🚀**
