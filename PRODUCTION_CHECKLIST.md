# Production Deployment Checklist

Quick reference for deploying Restaurant AI to production safely.

## Critical Security (MUST DO)

### 1. Generate Strong SECRET_KEY

```bash
# Generate
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
export SECRET_KEY="<paste-generated-key-here>"
```

Or add to `.env`:
```env
SECRET_KEY=your-actual-secret-key-not-the-default
```

**Why:** Default secret key allows session hijacking and token forgery.

---

### 2. Restrict CORS Origins

```bash
# Set to your actual domain
export ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

Or in `.env`:
```env
ALLOWED_ORIGINS=https://restaurant.example.com
```

**Why:** `ALLOWED_ORIGINS=*` allows any website to call your API (security risk).

---

### 3. Set Production Environment

```env
ENVIRONMENT=production
DEBUG=False
```

**Why:** Disables debug mode and enables production optimizations.

---

## Recommended (SHOULD DO)

### 4. Use HTTPS

Use a reverse proxy (nginx, Caddy, or AWS ALB):

```nginx
server {
    listen 443 ssl;
    server_name restaurant.example.com;

    ssl_certificate /etc/letsencrypt/live/restaurant.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/restaurant.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Why:** Protects data in transit, prevents MITM attacks.

---

### 5. Add Rate Limiting

Install:
```bash
pip install slowapi
```

Add to `requirements.txt`:
```
slowapi==0.1.9
```

Update `app/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, message: ChatRequest):
    # ... existing code
```

**Why:** Prevents DoS attacks and API abuse.

---

### 6. Enable Security Headers

Add to `app/main.py`:
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Why:** Protects against XSS, clickjacking, and MIME sniffing attacks.

---

## Infrastructure (SHOULD DO)

### 7. Set Up Monitoring

**Application Monitoring:**
- Health checks: `GET /health` every 30 seconds
- Log aggregation: CloudWatch, Datadog, or Sentry
- Uptime monitoring: UptimeRobot, Pingdom

**Resource Monitoring:**
- CPU usage < 80%
- Memory usage < 80%
- Disk space > 20% free

---

### 8. Configure Automated Backups

**SQLite (current):**
```bash
# Cron job for daily backups
0 2 * * * cp /app/data/orders.db /backups/orders-$(date +\%Y\%m\%d).db
```

**PostgreSQL (if migrated):**
```bash
# pg_dump daily
0 2 * * * pg_dump $DATABASE_URL > /backups/db-$(date +\%Y\%m\%d).sql
```

---

### 9. Enable Auto-Restart on Failure

**Docker Compose:**
```yaml
services:
  app:
    restart: unless-stopped  # ✅ Already configured
```

**Systemd (if not using Docker):**
```ini
[Service]
Restart=always
RestartSec=10
```

---

## Optional Enhancements

### 10. Add Dependency Scanning

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

### 11. Set Up CI/CD Deployment

**GitHub Actions for EC2:**
```yaml
name: Deploy to EC2

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/ubuntu/restaurant-ai-chatbot
            git pull
            docker compose up -d --build
```

---

## Quick Deployment Commands

### EC2 Deployment (with AI)

```bash
# 1. Launch EC2 instance (t3.medium, Ubuntu 24.04)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@<EC2_IP>

# 3. Run automated setup
wget https://raw.githubusercontent.com/Erics38/restaurant-ai-chatbot/main/scripts/ec2-setup-with-ai.sh
chmod +x ec2-setup-with-ai.sh
./ec2-setup-with-ai.sh

# 4. Set production environment variables
cat > .env << EOF
ENVIRONMENT=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ALLOWED_ORIGINS=https://yourdomain.com
DEBUG=False
EOF

# 5. Restart with production settings
docker compose down
docker compose up -d
```

---

### Local Docker Deployment

```bash
# 1. Clone repository
git clone https://github.com/Erics38/restaurant-ai-chatbot.git
cd restaurant-ai-chatbot

# 2. Create .env file
cp .env.example .env
nano .env  # Edit SECRET_KEY and ALLOWED_ORIGINS

# 3. Start application
docker compose up -d

# 4. Check logs
docker compose logs -f
```

---

## Verification After Deployment

```bash
# 1. Check health endpoint
curl https://yourdomain.com/health
# Expected: {"status":"healthy","environment":"production",...}

# 2. Check CORS headers
curl -I https://yourdomain.com/menu
# Should NOT see: Access-Control-Allow-Origin: *

# 3. Test rate limiting
for i in {1..15}; do curl https://yourdomain.com/menu; done
# Should get 429 Too Many Requests after 10 requests

# 4. Check security headers
curl -I https://yourdomain.com
# Should see: X-Content-Type-Options, X-Frame-Options, etc.

# 5. Test chat endpoint
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
# Should get valid response
```

---

## Rollback Plan

If deployment fails:

```bash
# 1. Check logs
docker compose logs app
docker compose logs llama-server

# 2. Rollback to previous version
git checkout <previous-commit>
docker compose up -d --build

# 3. Or stop everything
docker compose down

# 4. Check systemd logs (if applicable)
journalctl -u restaurant-ai -n 50
```

---

## Support Contacts

- **CI/CD Issues:** Check [CICD_SETUP.md](CICD_SETUP.md)
- **Security Issues:** See [SECURITY.md](SECURITY.md)
- **Deployment Issues:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **GitHub Issues:** https://github.com/Erics38/restaurant-ai-chatbot/issues

---

## Summary

**Minimum viable production deployment:**

1. ✅ Set `SECRET_KEY` to random value
2. ✅ Set `ALLOWED_ORIGINS` to your domain
3. ✅ Set `ENVIRONMENT=production`
4. ✅ Use HTTPS (reverse proxy)
5. ✅ Monitor health endpoint

**Time to deploy:** ~15 minutes
**Cost:** ~$30/month (t3.medium EC2) or $0.05/hour
