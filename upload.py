import boto3
from botocore.exceptions import ClientError
import os
import json

# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #
ec2 = boto3.client('ec2')
AMI_ID = "ami-04de2b60dd25fbb2e"
no_of_instances = 1
# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #

# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #
def runInstances():
    os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --count 1 --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup"')

def queryInstances():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress]' --output json > instances.json")
    f = open("instances.json","r")
    instances = json.load(f)
    for i in instances:
        for instance_id in i:
            print(instance_id[0])

def endInstances():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress]' --output json > instances.json")
    #loop through and terminate all instances
    f = open("instances.json","r")
    instances = json.load(f)
    for i in instances:
        for info in i:
            instance_id = info[0]
            try:
                response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #


endInstances()

# os.system('python find_nonce.py 0 100 3')