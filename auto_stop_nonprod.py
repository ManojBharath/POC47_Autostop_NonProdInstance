import boto3

REGION = "ap-south-2"
PROFILE = "authprofile"

# Initialize session with profile and create EC2 client
session = boto3.Session(profile_name=PROFILE)
ec2 = session.client('ec2', region_name=REGION)

def get_nonprod_instances():
    """
    Get all EC2 instances with 'Non-prod server' tag
    """
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['Non-prod server']
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'InstanceId': instance['InstanceId'],
                'Name': instance['Tags'][0]['Value'] if instance.get('Tags') else 'N/A',
                'State': instance['State']['Name']
            })
    
    return instances

def stop_instances(instance_ids):
    """
    Stop the given EC2 instances
    """
    if not instance_ids:
        print("No non-prod instances to stop.")
        return
    
    try:
        ec2.stop_instances(InstanceIds=instance_ids)
        print(f"Successfully stopped {len(instance_ids)} instance(s): {instance_ids}")
    except Exception as e:
        print(f"Error stopping instances: {str(e)}")

def main():
    print("Looking for non-prod instances to stop...")
    print(f"Region: {REGION}")
    print(f"Profile: {PROFILE}")
    
    # Test connection
    try:
        info = ec2.describe_instances(MaxResults=5)
        print("✓ AWS connection successful")
    except Exception as e:
        print(f"✗ AWS connection failed: {str(e)}")
        return
    
    # Get non-prod instances
    nonprod_instances = get_nonprod_instances()
    
    if not nonprod_instances:
        print("No running non-prod instances found.")
        return
    
    print(f"Found {len(nonprod_instances)} non-prod instance(s):")
    for instance in nonprod_instances:
        print(f"  - Instance ID: {instance['InstanceId']}, Name: {instance['Name']}, State: {instance['State']}")
    
    # Stop the instances
    instance_ids = [inst['InstanceId'] for inst in nonprod_instances]
    stop_instances(instance_ids)

if __name__ == "__main__":
    main()
    
