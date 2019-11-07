import boto3
from botocore.exceptions import ClientError
import os
import json

# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #
ec2 = boto3.client('ec2')
AMI_ID = "ami-04de2b60dd25fbb2e"
no_of_instances = 1
DNS_name = []
iam_role_name = "EnablesEC2ToAccessSystemsManagerRole"

directory = "Documents/University/4th/Cloud\ Computing"
# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #

# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #
def sendFile():
    for dns in DNS_name:
        os.system("scp -i ~/{}/MyFirstKey.pem ~/{}/find_nonce.py ec2-user@{}:/home/ec2-user".format(directory, directory, dns))
        # os.system("scp -i MyFirstKey.pem find_nonce.py ubuntu@ec2-{}.compute-1.amazonaws.com:~/data/".format(ip))
    
    # This is working fam.
        # os.system("scp -i ~/Documents/University/4th/Cloud\ Computing/MyFirstKey.pem ~/Documents/University/4th/Cloud\ Computing/find_nonce.py ec2-user@ec2-3-10-169-78.eu-west-2.compute.amazonaws.com:/home/ec2-user")

def runInstances(i):
    os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --iam-instance-profile Name={} --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" > output_run.json'.format(iam_role_name, i))
    # os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" --user-data://job.sh > output_run.json'.format(i))

def queryInstances():
    os.system("aws ec2 describe-instances --output json > instances-raw.json")

def findDNS():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress,PublicDnsName]' --output json > instances.json")
    f = open("instances.json","r")
    instances = json.load(f)
    for i in instances:
        for instance_id in i:
            attachIAMRole(instance_id[0])
            DNS_name.append(instance_id[5])

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

def attachIAMRole(instance_id):
    os.system("aws ec2 associate-iam-instance-profile --instance-id {} --iam-instance-profile Name={}".format(instance_id,iam_role_name))

def wait(instance_id, region):
    for i in range(DNS_name.count()):
        not_initialised = False
        while(not_initialised):
            ec2_resource = boto3.resource('ec2', region_name=region)
            instance = ec2_resource.Instance(instance_id)
            if (instance.state['Name'] == 'running'):
                not_initialised = True
                print("Instance {} up and running".format(i))
# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #



# endInstances()
runInstances(1)
# print("Instances ran.")
# findDNS()
# print("DNS Found.")
# sendFile()
# print("File Sent.")

# os.system('python find_nonce.py 0 100 3')