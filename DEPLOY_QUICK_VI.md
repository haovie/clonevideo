# 🚀 HƯỚNG DẪN DEPLOY LÊN DIGITAL OCEAN - NHANH

## Bước 1: Chuẩn bị (trên máy local)

```bash
# 1. Đảm bảo có file .env
cp .env.example .env
nano .env  # Điền đầy đủ thông tin

# 2. Test local (optional)
docker-compose up -d
docker-compose logs -f
docker-compose down  # Nếu OK
```

## Bước 2: Deploy (1 lệnh)

```bash
# Thay YOUR_DROPLET_IP bằng IP thật của bạn
./deploy_to_droplet.sh YOUR_DROPLET_IP

# Ví dụ:
./deploy_to_droplet.sh 104.248.123.45
```

Script sẽ tự động:
- ✅ Cài Docker & Docker Compose
- ✅ Copy files lên server
- ✅ Build Docker image
- ✅ Start bot

## Bước 3: Xác thực lần đầu

```bash
# SSH vào droplet
ssh root@YOUR_DROPLET_IP

# Xem logs
cd /opt/telegram-bot
docker-compose logs -f

# Bot sẽ gửi code qua Telegram
# Nhập code khi được hỏi
```

## Bước 4: Setup Auto-start (optional)

```bash
# Trên droplet
cat > /etc/systemd/system/telegram-bot.service << 'EOF'
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

[Install]
WantedBy=multi-user.target
EOF

# Enable
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot
systemctl status telegram-bot
```

## Các lệnh thường dùng

```bash
# SSH vào
ssh root@YOUR_DROPLET_IP

# Vào thư mục project
cd /opt/telegram-bot

# Xem logs
docker-compose logs -f

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# Update bot (sau khi có code mới)
docker-compose down
git pull  # hoặc rsync từ local
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
systemctl status telegram-bot

# Clean downloads
rm -rf downloads/*

# Clean Docker
docker system prune -a
```

## Backup session (quan trọng!)

```bash
# Trên droplet
cd /opt/telegram-bot
tar -czf ~/telegram-bot-backup-$(date +%Y%m%d).tar.gz \
    session_data/ allowed_users.json .env

# Download về local
# Trên máy local:
scp root@YOUR_DROPLET_IP:~/telegram-bot-backup-*.tar.gz ./
```

## Troubleshooting

### Bot không start
```bash
docker-compose logs
systemctl status docker
docker-compose restart
```

### Hết dung lượng
```bash
df -h
rm -rf /opt/telegram-bot/downloads/*
docker system prune -a
```

### Session hết hạn
```bash
cd /opt/telegram-bot
docker-compose down
rm -rf session_data/*
docker-compose up -d
docker-compose logs -f
# Authenticate lại
```

## Update bot từ local

```bash
# Trên máy local
rsync -avz --progress \
    --exclude='session_data/' \
    --exclude='downloads/' \
    --exclude='env-download-bot/' \
    --exclude='web-app/' \
    ./ root@YOUR_DROPLET_IP:/opt/telegram-bot/

# SSH vào và restart
ssh root@YOUR_DROPLET_IP 'cd /opt/telegram-bot && docker-compose down && docker-compose build && docker-compose up -d'
```

---

**Xong! Bot đang chạy trên cloud! ☁️**

Chi tiết hơn: đọc `DEPLOY_DIGITALOCEAN.md`
