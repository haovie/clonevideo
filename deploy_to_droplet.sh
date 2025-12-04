#!/bin/bash
# Deploy Telegram Bot to Digital Ocean Droplet

set -e

echo "🚀 Deploying Telegram Bot to Digital Ocean Droplet"
echo ""

# Configuration
DROPLET_IP="${1:-}"
DROPLET_USER="${2:-root}"
PROJECT_DIR="/opt/telegram-bot"

if [ -z "$DROPLET_IP" ]; then
    echo "❌ Error: Droplet IP is required"
    echo ""
    echo "Usage: ./deploy_to_droplet.sh <DROPLET_IP> [USER]"
    echo ""
    echo "Example:"
    echo "  ./deploy_to_droplet.sh 104.248.123.45"
    echo "  ./deploy_to_droplet.sh 104.248.123.45 root"
    exit 1
fi

echo "📋 Configuration:"
echo "  Droplet IP: $DROPLET_IP"
echo "  User: $DROPLET_USER"
echo "  Project Dir: $PROJECT_DIR"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file first: cp .env.example .env"
    exit 1
fi

echo "1️⃣  Installing Docker on Droplet (if needed)..."
ssh ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    echo "✅ Docker already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi
EOF

echo ""
echo "2️⃣  Creating project directory..."
ssh ${DROPLET_USER}@${DROPLET_IP} "mkdir -p ${PROJECT_DIR}"

echo ""
echo "3️⃣  Copying files to Droplet..."
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
    ./ ${DROPLET_USER}@${DROPLET_IP}:${PROJECT_DIR}/

echo ""
echo "4️⃣  Setting up directories..."
ssh ${DROPLET_USER}@${DROPLET_IP} << EOF
cd ${PROJECT_DIR}
mkdir -p session_data downloads
chmod 755 session_data downloads
EOF

echo ""
echo "5️⃣  Building Docker image..."
ssh ${DROPLET_USER}@${DROPLET_IP} << EOF
cd ${PROJECT_DIR}
docker-compose build
EOF

echo ""
echo "6️⃣  Starting bot..."
ssh ${DROPLET_USER}@${DROPLET_IP} << EOF
cd ${PROJECT_DIR}
docker-compose up -d
EOF

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Check logs: ssh ${DROPLET_USER}@${DROPLET_IP} 'cd ${PROJECT_DIR} && docker-compose logs -f'"
echo "  2. Check status: ssh ${DROPLET_USER}@${DROPLET_IP} 'cd ${PROJECT_DIR} && docker-compose ps'"
echo ""
echo "🔧 Useful commands:"
echo "  SSH to droplet: ssh ${DROPLET_USER}@${DROPLET_IP}"
echo "  View logs: cd ${PROJECT_DIR} && docker-compose logs -f"
echo "  Restart: cd ${PROJECT_DIR} && docker-compose restart"
echo "  Stop: cd ${PROJECT_DIR} && docker-compose down"
echo ""
