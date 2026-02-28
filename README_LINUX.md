# Non-Prod EC2 Auto Stop/Start Service - Linux Setup Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Workflow Diagram](#workflow-diagram)
4. [Prerequisites](#prerequisites)
5. [Linux Environment Setup](#linux-environment-setup)
6. [AWS Credentials Configuration](#aws-credentials-configuration)
7. [Python Installation & Setup](#python-installation--setup)
8. [Running the Scripts](#running-the-scripts)
9. [Auto-Trigger Setup (Linux Cron & Systemd)](#auto-trigger-setup-linux-cron--systemd)
10. [Logging and Monitoring](#logging-and-monitoring)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This project provides automated management of AWS EC2 Non-Prod instances on Linux platforms:

- **`auto_stop_nonprod.py`** - Manual script to stop running Non-Prod instances
- **`schedule_start_stop_nonprod.py`** - Automated scheduler that:
  - Stops Non-Prod instances daily at **9:00 PM** (21:00)
  - Starts Non-Prod instances daily at **9:00 AM** (09:00)
  - Logs all activities to `nonprod_scheduler.log`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Account (ap-south-2)                     │
│                                                                  │
│  ┌──────────────────────┐        ┌──────────────────────┐      │
│  │  Prod EC2 Instance   │        │ Non-Prod EC2 Instance│      │
│  │  (Tag: Prod server)  │        │(Tag: Non-prod server)│      │
│  │  Manual Management   │        │  Auto Stop/Start      │      │
│  └──────────────────────┘        └──────────────────────┘      │
│           │                              │                      │
│           └──────────────┬───────────────┘                      │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                    AWS API (boto3)
                           │
    ┌──────────────────────┴──────────────────────┐
    │                                             │
┌───▼──────────────────────┐      ┌──────────────▼─────┐
│  Linux Server/VM         │      │  Cron/Systemd      │
│  ┌────────────────────┐  │      │  (Auto-trigger)    │
│  │ auto_stop_nonprod  │  │      └────────┬───────────┘
│  │ .py (manual)       │  │              │
│  └────────────────────┘  │              │
│  ┌────────────────────┐  │      ┌───────▼────────┐
│  │ schedule_start_    │  │      │  9 AM Start    │
│  │ stop_nonprod.py    │  │      │  9 PM Stop     │
│  │ (auto-scheduler)   │  │      └────────────────┘
│  └────────────────────┘  │
│  ┌────────────────────┐  │
│  │ nonprod_scheduler  │  │
│  │ .log (logs)        │  │
│  └────────────────────┘  │
└──────────────────────────┘
```

---

## Workflow Diagram

```
START
  │
  ├─► Manual Execution: python auto_stop_nonprod.py
  │   └─► Immediately stop all running Non-Prod instances
  │
  └─► Automated Execution (Cron/Systemd)
      │
      ├─► 9:00 AM (09:00)
      │   └─► Start stopped Non-Prod instances
      │       └─► Log: "Successfully started instances"
      │
      └─► 9:00 PM (21:00)
          └─► Stop running Non-Prod instances
              └─► Log: "Successfully stopped instances"

Activity Flow:
┌─────────────┐
│  Scheduler  │
│   Started   │
└──────┬──────┘
       │
       ├──► Fetch instances with tag "Non-prod server"
       │
       ├──► Check instance state (running/stopped)
       │
       ├──► Execute start/stop action
       │
       └──► Log to nonprod_scheduler.log
```

---

## Prerequisites

### 1. Linux Distribution Support
- **Ubuntu 20.04+**
- **Debian 10+**
- **CentOS 7+**
- **RHEL 7+**
- **Amazon Linux 2**

### 2. AWS Account Setup
- Active AWS account with EC2 permissions
- Access Key ID and Secret Access Key
- EC2 instances tagged with `Name: "Non-prod server"`
- Instances in `ap-south-2` region (configurable)

### 3. Software Requirements
- Python 3.8+ installed
- pip (Python package manager)
- AWS CLI (optional but recommended)
- curl or wget (for downloads)

### 4. System Requirements
- Internet connectivity to AWS API
- sudo/root access (for systemd service setup)
- Cron daemon running (for scheduled tasks)

---

## Linux Environment Setup

### Step 1: Update System Packages

```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get upgrade -y

# For CentOS/RHEL
sudo yum update -y

# For Amazon Linux
sudo yum update -y
```

### Step 2: Install Python and pip

**Ubuntu/Debian:**
```bash
sudo apt-get install python3 python3-pip python3-venv -y
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip python3-venv -y
```

**Amazon Linux:**
```bash
sudo yum install python3 python3-pip -y
```

### Step 3: Verify Python Installation

```bash
python3 --version
pip3 --version
```

Expected output:
```
Python 3.8.10 (or higher)
pip 20.0.2 (or higher)
```

### Step 4: Create Project Directory

```bash
# Navigate to home directory
cd ~

# Create project folder
mkdir -p /opt/ec2-scheduler
cd /opt/ec2-scheduler

# Create subdirectories
mkdir -p logs scripts venv
```

### Step 5: Copy Project Files

```bash
# Option 1: Clone from Git
git clone <your-repo-url> /opt/ec2-scheduler

# Option 2: Copy files manually
cp auto_stop_nonprod.py /opt/ec2-scheduler/scripts/
cp schedule_start_stop_nonprod.py /opt/ec2-scheduler/scripts/
cp requirements.txt /opt/ec2-scheduler/
```

---

## AWS Credentials Configuration

### Option 1: Using AWS CLI (Recommended)

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Configure credentials
aws configure --profile authprofile
```

When prompted, enter:
- **AWS Access Key ID**: [Your Access Key]
- **AWS Secret Access Key**: [Your Secret Key]
- **Default region**: `ap-south-2`
- **Default output format**: `json`

### Option 2: Manual Configuration

Create credentials file:

```bash
# Create .aws directory if it doesn't exist
mkdir -p ~/.aws

# Create credentials file
cat > ~/.aws/credentials << EOF
[authprofile]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
EOF

# Set appropriate permissions
chmod 600 ~/.aws/credentials
```

Create config file:

```bash
cat > ~/.aws/config << EOF
[profile authprofile]
region = ap-south-2
output = json
EOF

chmod 600 ~/.aws/config
```

### Step 3: Verify Credentials

```bash
aws sts get-caller-identity --profile authprofile
```

Expected output:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

---

## Python Installation & Setup

### Step 1: Create Virtual Environment

```bash
cd /opt/ec2-scheduler

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Or manually
pip install boto3 apscheduler
```

### Step 3: Verify Installation

```bash
python -c "import boto3; import apscheduler; print('✓ All packages installed successfully')"
```

### Step 4: Deactivate Virtual Environment (Optional)

```bash
deactivate
```

---

## Running the Scripts

### Script 1: Manual Stop (auto_stop_nonprod.py)

Immediately stops all running Non-Prod instances:

```bash
# Activate virtual environment
cd /opt/ec2-scheduler
source venv/bin/activate

# Run script
python scripts/auto_stop_nonprod.py
```

**Output:**
```
Looking for non-prod instances to stop...
Region: ap-south-2
Profile: authprofile
✓ AWS connection successful
Found 1 non-prod instance(s):
  - Instance ID: i-0123456789abcdef0, Name: Non-prod server, State: running
Successfully stopped 1 instance(s): ['i-0123456789abcdef0']
```

---

### Script 2: Automated Scheduler (schedule_start_stop_nonprod.py)

Runs continuously and automatically stops/starts instances on schedule:

```bash
# Activate virtual environment
cd /opt/ec2-scheduler
source venv/bin/activate

# Run scheduler
python scripts/schedule_start_stop_nonprod.py
```

Press `Ctrl+C` to stop the scheduler.

---

## Auto-Trigger Setup (Linux Cron & Systemd)

### Method 1: Using Cron (Simpler)

#### Create Startup Script

```bash
# Create shell script to run scheduler
cat > /opt/ec2-scheduler/start_scheduler.sh << 'EOF'
#!/bin/bash

# Non-Prod EC2 Scheduler Startup Script
cd /opt/ec2-scheduler
source venv/bin/activate
python scripts/schedule_start_stop_nonprod.py >> logs/scheduler.log 2>&1 &

# Log startup
echo "$(date): Scheduler started" >> logs/startup.log
EOF

# Make script executable
chmod +x /opt/ec2-scheduler/start_scheduler.sh
```

#### Add to Crontab

```bash
# Edit crontab
crontab -e

# Add this line to run scheduler at system boot
@reboot /opt/ec2-scheduler/start_scheduler.sh

# Test crontab entry
crontab -l
```

#### For System-wide Execution (require sudo)

```bash
# Edit system crontab
sudo crontab -e

# Add line
@reboot /opt/ec2-scheduler/start_scheduler.sh
```

---

### Method 2: Using Systemd Service (Recommended)

#### Create Systemd Service File

```bash
# Create service file
sudo cat > /etc/systemd/system/ec2-scheduler.service << 'EOF'
[Unit]
Description=Non-Prod EC2 Auto Start/Stop Scheduler
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/ec2-scheduler
ExecStart=/opt/ec2-scheduler/venv/bin/python /opt/ec2-scheduler/scripts/schedule_start_stop_nonprod.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/opt/ec2-scheduler/logs/scheduler.log
StandardError=append:/opt/ec2-scheduler/logs/scheduler.log
Environment="PATH=/opt/ec2-scheduler/venv/bin"

[Install]
WantedBy=multi-user.target
EOF
```

> **Note:** Change `User=ubuntu` to your actual Linux user

#### Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start at boot
sudo systemctl enable ec2-scheduler.service

# Start service immediately
sudo systemctl start ec2-scheduler.service

# Check service status
sudo systemctl status ec2-scheduler.service

# View service logs
sudo journalctl -u ec2-scheduler.service -f
```

#### Service Management Commands

```bash
# Check if service is running
sudo systemctl is-active ec2-scheduler.service

# Restart service
sudo systemctl restart ec2-scheduler.service

# Stop service
sudo systemctl stop ec2-scheduler.service

# View recent logs
sudo journalctl -u ec2-scheduler.service --since "1 hour ago"

# View all logs
sudo journalctl -u ec2-scheduler.service -n 100
```

---

## Logging and Monitoring

### Log File Locations

```
/opt/ec2-scheduler/logs/scheduler.log      # Main scheduler log
/opt/ec2-scheduler/logs/startup.log        # Cron startup log (if using cron)
/var/log/syslog                            # System logs (includes systemd output)
```

### View Logs

```bash
# View real-time logs (follow mode)
tail -f /opt/ec2-scheduler/logs/scheduler.log

# View last 50 lines
tail -50 /opt/ec2-scheduler/logs/scheduler.log

# Search for errors
grep -i "error" /opt/ec2-scheduler/logs/scheduler.log

# Search for successful actions
grep -i "successfully" /opt/ec2-scheduler/logs/scheduler.log

# View systemd logs
sudo journalctl -u ec2-scheduler.service -f

# View logs from specific date
sudo journalctl -u ec2-scheduler.service --since "2026-02-28 10:00:00"
```

### Sample Log Output

```
2026-02-28 21:00:05,123 - INFO - ============================================================
2026-02-28 21:00:05,125 - INFO - SCHEDULED TASK: Stopping Non-Prod instances at 9 PM
2026-02-28 21:00:05,127 - INFO - ============================================================
2026-02-28 21:00:05,500 - INFO - ✓ Successfully stopped 1 Non-prod instance(s)
2026-02-28 21:00:05,502 - INFO -   - Instance ID: i-0123456789abcdef0, Name: Non-prod server
```

### Monitoring Dashboard Commands

```bash
# Real-time service status
watch -n 5 'sudo systemctl status ec2-scheduler.service'

# Monitor logs with timestamps
sudo journalctl -u ec2-scheduler.service --since "5 minutes ago" -f --no-pager

# Count of stop/start operations
grep -c "Successfully stopped\|Successfully started" /opt/ec2-scheduler/logs/scheduler.log
```

---

## Troubleshooting

### Issue 1: Service Fails to Start

**Troubleshooting:**
```bash
# Check service status
sudo systemctl status ec2-scheduler.service

# Check for errors
sudo journalctl -u ec2-scheduler.service -n 50

# Verify Python path
which python3
echo $PATH

# Test script manually
cd /opt/ec2-scheduler
source venv/bin/activate
python scripts/schedule_start_stop_nonprod.py
```

---

### Issue 2: AWS Credentials Not Found

**Error:**
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solution:**
```bash
# Verify credentials file exists
test -f ~/.aws/credentials && echo "✓ Credentials file found" || echo "✗ Credentials file missing"

# Check credentials file content
cat ~/.aws/credentials

# Verify config file
cat ~/.aws/config

# Test AWS connection
aws sts get-caller-identity --profile authprofile

# If using systemd, ensure AWS credentials accessible to service user
sudo -u <service-user> aws sts get-caller-identity --profile authprofile
```

---

### Issue 3: Permission Denied Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix file permissions
chmod 755 /opt/ec2-scheduler
chmod 755 /opt/ec2-scheduler/scripts
chmod 644 /opt/ec2-scheduler/scripts/*.py

# Fix directory ownership (if using systemd)
sudo chown -R ubuntu:ubuntu /opt/ec2-scheduler

# Fix log directory
mkdir -p /opt/ec2-scheduler/logs
chmod 755 /opt/ec2-scheduler/logs
```

---

### Issue 4: Cron Job Not Executing

**Error:** Scheduler not running after reboot

**Troubleshooting:**
```bash
# Check if cron service is running
sudo systemctl status cron

# Verify crontab entry
crontab -l

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Test cron manually
*/5 * * * * /opt/ec2-scheduler/start_scheduler.sh

# Output full paths in cron (not using environment variables)
@reboot /bin/bash -c 'source /opt/ec2-scheduler/venv/bin/activate && /opt/ec2-scheduler/venv/bin/python /opt/ec2-scheduler/scripts/schedule_start_stop_nonprod.py'
```

---

### Issue 5: Instances Not Stopping/Starting

**Check:**
1. Verify EC2 instances exist and have correct tag:
   ```bash
   aws ec2 describe-instances --region ap-south-2 --profile authprofile \
     --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0],State.Name]' \
     --output table
   ```

2. Check IAM permissions:
   ```bash
   aws ec2 describe-instances --region ap-south-2 --profile authprofile --max-results 5
   ```

3. Check logs for errors:
   ```bash
   grep -i "error\|invalid" /opt/ec2-scheduler/logs/scheduler.log
   ```

4. Verify Python can import boto3:
   ```bash
   /opt/ec2-scheduler/venv/bin/python -c "import boto3; print('✓ boto3 available')"
   ```

---

## Configuration Changes

### Change Stop/Start Times

Edit `schedule_start_stop_nonprod.py`:

```python
# Line 118-126
# Schedule stop at different time (e.g., 11 PM = 23:00)
scheduler.add_job(
    stop_nonprod_instances,
    CronTrigger(hour=23, minute=0),  # Change 21 to 23 for 11 PM
    id='stop_nonprod_9pm',
    name='Stop Non-Prod at 11 PM',
    replace_existing=True
)
```

Then restart service:
```bash
sudo systemctl restart ec2-scheduler.service
```

---

### Change Region

Edit both Python files:

```bash
# Edit auto_stop_nonprod.py
sed -i 's/REGION = "ap-south-2"/REGION = "us-east-1"/' scripts/auto_stop_nonprod.py

# Edit schedule_start_stop_nonprod.py
sed -i 's/REGION = "ap-south-2"/REGION = "us-east-1"/' scripts/schedule_start_stop_nonprod.py
```

---

### Change Instance Tag

Edit both Python files:

```bash
# Change tag name
sed -i 's/INSTANCE_TAG_NAME = "Non-prod server"/INSTANCE_TAG_NAME = "YourTagName"/' scripts/schedule_start_stop_nonprod.py
```

---

## Quick Start Summary

```bash
# 1. Create directory
sudo mkdir -p /opt/ec2-scheduler
cd /opt/ec2-scheduler

# 2. Copy project files
sudo cp auto_stop_nonprod.py schedule_start_stop_nonprod.py requirements.txt /opt/ec2-scheduler/

# 3. Create virtual environment
python3 -m venv venv

# 4. Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure AWS credentials
aws configure --profile authprofile

# 6. Test manual script
python scripts/auto_stop_nonprod.py

# 7. Create systemd service
sudo cp ec2-scheduler.service /etc/systemd/system/

# 8. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ec2-scheduler.service
sudo systemctl start ec2-scheduler.service

# 9. Verify service
sudo systemctl status ec2-scheduler.service
```

---

## Additional Resources

- **AWS Documentation:** https://docs.aws.amazon.com/ec2/
- **Boto3 Documentation:** https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **APScheduler Documentation:** https://apscheduler.readthedocs.io/
- **Systemd Documentation:** https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **Cron Documentation:** http://crontab.guru/

---

## Summary Checklist

- [ ] Linux system updated
- [ ] Python 3.8+ installed
- [ ] Project directory created at `/opt/ec2-scheduler`
- [ ] Project files copied
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] AWS credentials configured
- [ ] AWS connection verified
- [ ] Manual script tested
- [ ] Scheduler script tested
- [ ] Systemd service created (or cron job)
- [ ] Service enabled and started
- [ ] Logs verified
- [ ] Service tested with reboot

---

**Last Updated:** February 28, 2026  
**Version:** 1.0  
**Platform:** Linux (Ubuntu, Debian, CentOS, RHEL, Amazon Linux)
