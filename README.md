This project provides simple Terraform scripts to create EC2 instances and a Python script to automatically stop non-production instances.

## Prerequisites

1. **AWS Account** with appropriate permissions to create/manage EC2 instances
2. **Terraform** installed (version 1.0+)
3. **Python** 3.7+ installed
4. **AWS CLI** configured with your credentials
5. **boto3** Python library
6. **EC2 Key Pair (.pem file)** - Place in your AWS account

## Setup Instructions

### Step 1: Prepare AWS Credentials

Ensure your AWS credentials are configured:
```bash
aws configure
```

### Step 2: Update Terraform Variables

Edit `main.tf` and replace:
- `ami-0c55b159cbfafe1f0` - Find the correct AMI ID for ap-south-2 region
- `your-key-pair-name` - Replace with your EC2 key pair name (without .pem extension)

### Step 3: Deploy Infrastructure with Terraform

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply
```

### Step 4: Install Python Dependencies

```bash
pip install boto3
```

### Step 5: Run Auto-Stop Script

```bash
python auto_stop_nonprod.py
```

## File Descriptions

- **main.tf** - Terraform configuration to create 2 EC2 instances (Prod and Non-prod) in ap-south-2 region
- **auto_stop_nonprod.py** - Python script to identify and stop non-prod instances
- **Requirements.txt** - Python dependencies

## How It Works

1. **Terraform** creates 2 EC2 instances with name tags:
   - "Prod server"
   - "Non-prod server"

2. **Python Script**:
   - Connects to AWS ap-south-2 region
   - Finds all instances tagged as "Non-prod server" in running state
   - Displays instance details
   - Stops the non-prod instances

## Region Info

- **Region**: ap-south-2 (Asia Pacific - Melbourne)
- Verify AMI availability in this region before deploying

## Schedule Auto-Stop (Optional)

To run the auto-stop script on a schedule:

**Windows (Task Scheduler)**:
- Create a scheduled task to run: `python auto_stop_nonprod.py`
- Set frequency as needed (daily, hourly, etc.)

**Linux/Mac (Cron)**:
```bash
0 22 * * * /usr/bin/python3 /path/to/auto_stop_nonprod.py
```

## Notes

- Ensure your AWS IAM user has permissions for `ec2:DescribeInstances` and `ec2:StopInstances`
- The script only stops running instances; it won't start them
- Always test in a non-production environment first
