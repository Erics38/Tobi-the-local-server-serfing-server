#!/bin/bash
# EC2 User Data Script - Restaurant AI Chatbot
# This script runs automatically when launching an EC2 instance
# It installs all dependencies and starts the application

set -e  # Exit on any error

echo "========================================"
echo "Starting Restaurant AI Setup on EC2"
echo "========================================"

# Update system
echo "[1/6] Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install Docker and Docker Compose
echo "[2/6] Installing Docker..."
apt-get install -y docker.io docker-compose git curl

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Install Python 3.11 for testing
echo "[3/6] Installing Python 3.11..."
apt-get install -y python3.11 python3.11-venv python3-pip

# Clone repository
echo "[4/6] Cloning restaurant-ai-chatbot..."
cd /home/ubuntu
git clone https://github.com/Erics38/restaurant-ai-chatbot.git
chown -R ubuntu:ubuntu restaurant-ai-chatbot
cd restaurant-ai-chatbot

# Start Docker Compose (template mode - no AI model needed)
echo "[5/6] Starting application with Docker..."
docker-compose up -d app

# Wait for app to be healthy
echo "[6/6] Waiting for application to start..."
sleep 10

# Check health
if curl -f http://localhost:8000/health; then
    echo ""
    echo "========================================"
    echo "✓ Restaurant AI is running!"
    echo "========================================"
    echo ""
    echo "Access the application:"
    echo "  Web UI:   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/static/restaurant_chat.html"
    echo "  API Docs: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/api/docs"
    echo "  Health:   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/health"
    echo ""
    echo "To run tests (SSH into instance):"
    echo "  cd /home/ubuntu/restaurant-ai-chatbot"
    echo "  sudo su - ubuntu"
    echo "  python3.11 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  pip install pytest pytest-asyncio black flake8 mypy"
    echo "  ./scripts/verify-ci-locally.sh"
else
    echo "ERROR: Application failed to start"
    echo "Check logs: docker-compose logs"
    exit 1
fi
