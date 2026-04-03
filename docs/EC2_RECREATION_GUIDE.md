# EC2 Instance Recreation Guide

## Quick Recreation (Without AMI)

Instead of paying for an AMI, you can recreate your EC2 setup in ~10 minutes using the automated script.

### What You Need to Save Locally

**Nothing!** Everything is in this Git repository:
- ✅ Setup script: `scripts/ec2-setup-with-ai.sh`
- ✅ User data script: `scripts/ec2-user-data.sh`
- ✅ Docker configuration: `docker-compose.yml`
- ✅ All source code

### Recreation Steps

#### Method 1: Automated Setup (Recommended)

1. **Launch New EC2 Instance:**
   - Instance Type: `t3.medium` (2 vCPU, 4GB RAM)
   - AMI: Ubuntu 24.04 LTS
   - Storage: 20GB gp3
   - Security Group: Allow SSH (22), HTTP (8000), Custom (8080)

2. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@<NEW_IP>
   ```

3. **Run the setup script:**
   ```bash
   wget https://raw.githubusercontent.com/Erics38/restaurant-ai-chatbot/main/scripts/ec2-setup-with-ai.sh
   chmod +x ec2-setup-with-ai.sh
   ./ec2-setup-with-ai.sh
   ```

4. **Wait ~10 minutes:**
   - System updates: ~2 min
   - Docker installation: ~1 min
   - Model download (4.92GB): ~5 min
   - Docker build: ~2 min
   - Services start: ~1 min

5. **Access your app:**
   - Open browser: `http://<NEW_IP>:8000/static/restaurant_chat.html`

**Total time: ~10 minutes**
**Cost: $0** (just terminate when done)

---

#### Method 2: Use EC2 User Data (Fully Automated)

Launch instance with this user data script to automate everything:

1. **Launch EC2 with User Data:**
   - Go to EC2 Console → Launch Instance
   - Choose Ubuntu 24.04 LTS
   - Instance type: t3.medium
   - Under "Advanced details" → "User data", paste:

```bash
#!/bin/bash
# Download and run setup script
cd /home/ubuntu
wget https://raw.githubusercontent.com/Erics38/restaurant-ai-chatbot/main/scripts/ec2-setup-with-ai.sh
chmod +x ec2-setup-with-ai.sh
sudo -u ubuntu ./ec2-setup-with-ai.sh
```

2. **Launch instance**

3. **Wait ~12 minutes for setup to complete**

4. **Check logs (optional):**
   ```bash
   ssh -i your-key.pem ubuntu@<NEW_IP>
   tail -f /var/log/cloud-init-output.log
   ```

**Total time: ~12 minutes** (fully automated)

---

### What Gets Recreated

✅ **Automatically recreated:**
- Docker + Docker Compose
- Python 3.12 + pip
- All Python dependencies
- Llama-3-8B AI model (downloaded from HuggingFace)
- Custom llama-server Docker image
- docker-compose.override.yml configuration
- All application code

❌ **NOT recreated (you'll lose):**
- Test orders in database (SQLite in `data/` folder)
- Log files
- Any custom changes you made directly on EC2

---

### Cost Comparison

| Method | Monthly Cost | Recreation Time | Notes |
|--------|-------------|-----------------|-------|
| **AMI** | ~$0.50 | 2 minutes | Saves exact state |
| **Stop Instance** | ~$2.00 | Instant | IP changes on restart |
| **Script Recreation** | $0.00 | 10 minutes | Fresh setup each time |
| **Running Instance** | ~$30.00 | N/A | Don't do this! |

**Recommendation:** Use script recreation (free) unless you need to save specific data.

---

### Save Your Current Configuration (Optional)

If you made custom changes on EC2, save them locally:

1. **Save docker-compose.override.yml:**
   ```bash
   # On EC2
   cat /home/ubuntu/restaurant-ai-chatbot/docker-compose.override.yml

   # Copy the output and save it locally at:
   # C:\Users\syver\code\restaurant-ai-chatbot\docker-compose.override.yml
   ```

2. **Save any test data:**
   ```bash
   # On EC2
   scp -i your-key.pem ubuntu@<IP>:/home/ubuntu/restaurant-ai-chatbot/data/orders.db \
     C:\Users\syver\code\restaurant-ai-chatbot\data\
   ```

---

### Terminate Current Instance

Once you're ready:

1. **AWS Console → EC2 → Instances**
2. **Select your instance**
3. **Instance state → Terminate instance**
4. **Confirm**

Your instance will be gone in ~1 minute. You'll stop paying immediately.

---

### Next Time You Need It

Just run the setup script again! Everything is in Git.

```bash
# Fresh EC2 instance
wget https://raw.githubusercontent.com/Erics38/restaurant-ai-chatbot/main/scripts/ec2-setup-with-ai.sh
chmod +x ec2-setup-with-ai.sh
./ec2-setup-with-ai.sh
```

That's it! ✨
