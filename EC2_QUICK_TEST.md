# EC2 Quick Test Guide

Quick guide to test Restaurant AI on EC2 in under 5 minutes.

## Option 1: AWS Console (Easiest)

### Step 1: Launch Instance

1. Go to EC2 Dashboard: https://console.aws.amazon.com/ec2/
2. Click "Launch Instance"
3. Configure:
   - **Name**: `restaurant-ai-test`
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance type**: t3.medium (2 vCPU, 4GB RAM)
   - **Key pair**: Create new or select existing
   - **Security group**: Create new with these rules:
     - SSH (22) from your IP
     - HTTP (8000) from anywhere (0.0.0.0/0)
   - **Storage**: 20 GB gp3

### Step 2: Add User Data

Scroll to "Advanced details" → "User data" and paste this:

```bash
#!/bin/bash
set -e
apt-get update -y && apt-get upgrade -y
apt-get install -y docker.io docker-compose git curl python3.11 python3.11-venv python3-pip
systemctl enable docker && systemctl start docker
usermod -aG docker ubuntu
cd /home/ubuntu
git clone https://github.com/Erics38/restaurant-ai-chatbot.git
chown -R ubuntu:ubuntu restaurant-ai-chatbot
cd restaurant-ai-chatbot
docker-compose up -d app
sleep 10
curl -f http://localhost:8000/health && echo "✓ Application running!"
```

### Step 3: Launch and Wait

1. Click "Launch Instance"
2. Wait ~3 minutes for setup to complete
3. Go to instance details, copy "Public IPv4 address"

### Step 4: Access Application

Open in browser:
- **Web UI**: `http://YOUR_EC2_IP:8000/static/restaurant_chat.html`
- **API Docs**: `http://YOUR_EC2_IP:8000/api/docs`
- **Health Check**: `http://YOUR_EC2_IP:8000/health`

Should see: `{"status":"healthy","environment":"production","database":"n/a","version":"1.0.0"}`

### Step 5: Test Contributor Workflow (Optional)

SSH into instance:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

Run verification tests:

```bash
cd restaurant-ai-chatbot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy
./scripts/verify-ci-locally.sh
```

Expected: All 4 checks pass (Black, Flake8, MyPy, Pytest)

### Step 6: Cleanup

**IMPORTANT**: Terminate instance when done to avoid charges!

```bash
# AWS Console: Select instance → Instance State → Terminate
# OR via CLI:
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

**Cost**: ~$0.05/hour (t3.medium)

---

## Option 2: AWS CLI (Fastest)

### Prerequisites

```bash
aws configure  # Set up AWS credentials if not already done
```

### Launch Instance

```bash
# Create security group (one-time)
aws ec2 create-security-group \
  --group-name restaurant-ai-test \
  --description "Security group for Restaurant AI testing"

# Get your IP
MY_IP=$(curl -s https://checkip.amazonaws.com)

# Allow SSH from your IP
aws ec2 authorize-security-group-ingress \
  --group-name restaurant-ai-test \
  --protocol tcp --port 22 \
  --cidr $MY_IP/32

# Allow HTTP on port 8000 from anywhere
aws ec2 authorize-security-group-ingress \
  --group-name restaurant-ai-test \
  --protocol tcp --port 8000 \
  --cidr 0.0.0.0/0

# Launch instance with user data
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t3.medium \
  --key-name YOUR_KEY_NAME \
  --security-groups restaurant-ai-test \
  --user-data file://scripts/ec2-user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=restaurant-ai-test}]'
```

### Get Instance IP

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=restaurant-ai-test" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

### Access Application

```bash
# Save IP
EC2_IP=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=restaurant-ai-test" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# Check health
curl http://$EC2_IP:8000/health

# Open in browser
echo "Web UI: http://$EC2_IP:8000/static/restaurant_chat.html"
```

### Cleanup

```bash
# Get instance ID
INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=restaurant-ai-test" --query 'Reservations[0].Instances[0].InstanceId' --output text)

# Terminate
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
```

---

## Option 3: CloudFormation (For Later - AWS Portfolio)

Save this as `cloudformation/restaurant-ai-stack.yaml` when ready to showcase AWS skills:

```yaml
# Coming soon - will include:
# - VPC with public/private subnets
# - Application Load Balancer
# - ECS Fargate service
# - Auto-scaling
# - CloudWatch monitoring
# - S3 for static assets
# - CloudFront CDN
```

---

## Troubleshooting

### Application not accessible

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Check Docker status
sudo docker ps

# Check logs
cd /home/ubuntu/restaurant-ai-chatbot
sudo docker-compose logs app

# Restart if needed
sudo docker-compose restart app
```

### Health check fails

```bash
# Check if port 8000 is open
curl http://localhost:8000/health

# Check security group allows port 8000
# AWS Console → EC2 → Security Groups → restaurant-ai-test → Inbound rules
```

### User data didn't run

```bash
# SSH into instance and check logs
sudo cat /var/log/cloud-init-output.log
```

---

## Verification Checklist

After EC2 launch:

- [ ] Instance running (AWS Console shows "Running" state)
- [ ] Security group allows SSH (22) and HTTP (8000)
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Web UI loads in browser
- [ ] API docs accessible at `/api/docs`
- [ ] Chat sends messages (template responses work)
- [ ] SSH access works
- [ ] Tests pass with `./scripts/verify-ci-locally.sh`
- [ ] Instance terminated after testing (avoid charges!)

---

## Next Steps

After EC2 testing proves it works:

1. **CloudFormation Template** - Create full AWS infrastructure as code
2. **CI/CD Pipeline** - Add GitHub Actions workflow to deploy to AWS
3. **CloudFront CDN** - Add for frontend distribution
4. **Route53** - Add custom domain
5. **Certificate Manager** - Add HTTPS

See `CLOUDFORMATION_GUIDE.md` (coming soon) for production deployment.

---

## Cost Estimates

| Duration | Cost (t3.medium) |
|----------|------------------|
| 1 hour   | $0.05           |
| 8 hours  | $0.40           |
| 24 hours | $1.20           |
| 1 month  | $36.00          |

**Remember to terminate when done!**
