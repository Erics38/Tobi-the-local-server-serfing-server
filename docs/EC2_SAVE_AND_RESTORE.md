# EC2 Instance - Save and Restore Guide

## Saving Your EC2 Instance Before Termination

You have two options to save your work:

### Option 1: Create an AMI (Amazon Machine Image) ✅ Recommended

**Pros:**
- Saves exact state of instance (installed software, configurations, files)
- Can launch new instances from it instantly
- Free storage (~$0.05/GB/month for EBS snapshots)

**Steps:**

1. **Create AMI from AWS Console:**
   ```
   1. Go to EC2 Console → Instances
   2. Select your instance (i-xxxxx)
   3. Actions → Image and templates → Create image
   4. Image name: restaurant-ai-working-setup
   5. Description: Restaurant AI with Docker, AI model, all dependencies
   6. Click "Create image"
   ```

2. **Terminate Instance:**
   ```
   1. Select instance
   2. Instance state → Terminate instance
   ```

3. **Restore Later:**
   ```
   1. Go to EC2 → AMIs (left sidebar)
   2. Select restaurant-ai-working-setup
   3. Launch instance from AMI
   4. Choose same instance type (t3.medium)
   5. Same security group settings
   6. Launch
   ```

**Cost:** ~$0.50/month for AMI storage (10GB snapshot)

---

### Option 2: Stop Instance (Don't Terminate) ✅ Simpler but costs more

**Pros:**
- Super simple - just click "Stop"
- Everything preserved exactly as is
- Can restart anytime

**Cons:**
- EBS volume still charges (~$1/month for 20GB)
- Can't modify instance type without stopping

**Steps:**

1. **Stop Instance:**
   ```
   1. Go to EC2 Console → Instances
   2. Select instance
   3. Instance state → Stop instance
   4. Wait for state: stopped
   ```

2. **Restart Later:**
   ```
   1. Select instance
   2. Instance state → Start instance
   3. Note: Public IP will change!
   ```

**Cost:** ~$2/month for stopped instance (EBS storage only)

---

### Option 3: Save Work to GitHub (Free but requires manual setup)

**What to save:**

1. **Code changes** - already in Git
2. **Docker override file** - commit it
3. **Downloaded model** - document where to get it

**Steps:**

1. **SSH into instance and save override config:**
   ```bash
   # Copy the override file you created
   cat docker-compose.override.yml
   ```

2. **Commit the override example:**
   ```bash
   # On your local machine
   git add docker-compose.override.yml.example
   git add scripts/test-ai-model.sh
   git commit -m "docs: Add AI mode configuration and testing scripts"
   git push
   ```

3. **Document the model download:**
   - Already in docs (Meta-Llama-3-8B-Instruct.Q4_K_M.gguf from HuggingFace)

4. **Terminate instance:**
   ```
   All work is in Git, can recreate from scratch
   ```

**Cost:** $0 (but takes 30 min to set up again)

---

## Recommendation

**If you want to continue this exact work soon (within a week):**
→ Use **Option 1 (Create AMI)** - costs ~$0.50/month, instant restore

**If you're done testing and just want the code:**
→ Use **Option 3 (GitHub)** - free, recreate when needed

**If you want to pause for a few days:**
→ Use **Option 2 (Stop)** - costs ~$2/month, very simple

---

## What You'll Lose if You Just Terminate

- ✗ Installed Docker, Python, dependencies
- ✗ Downloaded Llama-3-8B model (4.92GB)
- ✗ Built Docker images (local-llama-server)
- ✗ docker-compose.override.yml configuration
- ✓ All code (safe in Git)
- ✓ Documentation (safe in Git)

---

## Quick Commands

### Create AMI (via AWS CLI):
```bash
aws ec2 create-image \
  --instance-id i-YOUR-INSTANCE-ID \
  --name "restaurant-ai-working-setup" \
  --description "Restaurant AI with Docker, Llama-3-8B model, ready to run"
```

### Stop Instance (via AWS CLI):
```bash
aws ec2 stop-instances --instance-ids i-YOUR-INSTANCE-ID
```

### Terminate Instance (via AWS CLI):
```bash
aws ec2 terminate-instances --instance-ids i-YOUR-INSTANCE-ID
```

---

## Current Instance Details

- Instance Type: t3.medium
- AMI: Ubuntu 24.04 LTS
- Storage: 20GB gp3
- What's Installed:
  - Docker + Docker Compose v2
  - Python 3.12 + venv
  - Llama-3-8B AI model (4.92GB)
  - Custom llama-server Docker image
  - All dependencies from requirements.txt

You can recreate this with the user data script, but you'll need to:
1. Re-download the Llama-3-8B model (~5 min)
2. Re-build the llama-server Docker image (~3 min)
3. Create docker-compose.override.yml

**Total recreation time: ~15-20 minutes**
**AMI restore time: ~2 minutes**
