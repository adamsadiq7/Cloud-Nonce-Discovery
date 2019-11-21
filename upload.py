import boto3
from botocore.exceptions import ClientError
import os
import json

# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #
ec2 = boto3.client('ec2')
client = boto3.client('ssm')
AMI_ID = "ami-04de2b60dd25fbb2e"
no_of_instances = 1
DNS_name = []
iam_role_name = "EnablesEC2ToAccessSystemsManagerRole"


directory = "Documents/University/4th/Cloud\ Computing"
# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #

# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #
def sendFile(dns):
    os.system("scp -i ~/{}/MyFirstKey.pem ~/{}/find_nonce.py ec2-user@{}:/home/ec2-user".format(directory, directory, dns))
        # os.system("scp -i MyFirstKey.pem find_nonce.py ubuntu@ec2-{}.compute-1.amazonaws.com:~/data/".format(ip))
    
    # This is working fam.
        # os.system("scp -i ~/Documents/University/4th/Cloud\ Computing/MyFirstKey.pem ~/Documents/University/4th/Cloud\ Computing/find_nonce.py ec2-user@ec2-3-10-169-78.eu-west-2.compute.amazonaws.com:/home/ec2-user")

def runInstances(i):
    os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --iam-instance-profile Name={} --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" > output_run.json'.format(iam_role_name, i))
    # os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" --user-data://job.sh > output_run.json'.format(i))

def queryInstances():
    os.system("aws ec2 describe-instances --output json > instances-raw.json")

def waitAndSend():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress,PublicDnsName]' --output json > instances.json")
    f = open("instances.json","r")
    instances = json.load(f)
    for i in instances:
        for instance_id in i:
            if (not(instance_id[1]['Name'] == 'terminated' or instance_id[1]['Name'] == 'shutting-down')):
                DNS_name.append(instance_id[5])
                wait(instance_id[0], 'eu-west-2') #wait until instance is running
                if (instance_id[1]['Name'] == 'running'):
                    sendFile(instance_id[5])
                    ssh(instance_id[5])

            # attachIAMRole(instance_id[0])
            # print(instance_id)
                # print(DNS_name.count())
                # if (not(instance_id[1]['Name'] == 'terminated' or instance_id[1]['Name'] == 'shutting-down')):
                # print(boto3.resource('ec2').Instance(instance_id[0]).monitor())

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

def ssh(dns):
    os.system("ssh -i /{}/MyFirstKey.pem ec2-user@{}".format(directory, dns))

def terminateInstances():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress]' --output json > instances.json")
    #loop through and terminate all instances
    f = open("instances.json","r")
    instances = json.load(f)
    for i in instances:
        for info in i:
            instance_id = info[0]
            try:
                response = ec2.terminate_instances(InstanceIds=[instance_id], DryRun=False)
                print(response)
            except ClientError as e:
                print(e)

def attachIAMRole(instance_id):
    os.system("aws ec2 associate-iam-instance-profile --instance-id {} --iam-instance-profile Name={}".format(instance_id,iam_role_name))

def wait(instance_id, region):
    print("Waiting for instance {}...".format(str(instance_id)))
    # print(str(instance_id))
    not_initialised = True
    while(not_initialised):
        ec2_resource = boto3.resource('ec2', region_name=region)
        # ec2_resource = boto3.resource('ec2')
        # ec2_resource.Instance(instance_id).wait_until_running()
        instance = ec2_resource.Instance(instance_id)

        response = ec2.describe_instance_status(
                InstanceIds=[
                    instance_id,
                ],
                DryRun=False,
                IncludeAllInstances=True|False
        )

        if (instance.state['Name'] == 'running' and (response['InstanceStatuses'][0]["SystemStatus"]["Status"]) == "ok"):
            not_initialised = False
            print("Instance {} up and running!".format(instance_id))
            print(json.dumps(response))
            sendCommand(instance_id, "AWS-RunShellScript")
        # else:
        #     print(instance.state['Name'])

def createSSMCommand():
    os.system("aws ssm create-document --content file:///home/ec2-user/RunShellScript.json  --name `RunShellScript` --document-type `Command`")


def sendCommand(instance_id, document_name):
    print("Running file...")
    # os.system('aws ssm send-command --instance-ids {} --document-name {} --comment "IP config" --parameters commands=ifconfig --output text'.format(instance_id, document_name))
    # os.system('sh_command_id=$(aws ssm send-command --instance-ids {} --document-name {} --comment "Demo run shell script on Linux Instance" --parameters commands=ls --output text --query "Command.CommandId"'.format(instance_id, document_name))

    # first = "aws ssm send-command --instance-ids {} --document-name AWS-RunShellScript --comment"
    # save this one lad
    # os.system('aws ssm send-command --instance-ids {} --output text --query \'Command.CommandId\' > adam.txt'.format(instance_id))

    print(type(str(instance_id)))

    response = client.send_command(
        InstanceIds=[
            str(instance_id),
        ],
        DocumentName=document_name,
        TimeoutSeconds=123,
        Comment='Try and Run find_nonce.py',
        Parameters={
            'commands': [
                'python find_nonce.py 0 10 0',
                "print \"Hello world from python\""
            ]
        }
    )
    print(response)

    # os.system('aws ssm send-command --instance-ids {} --document-name AWS-RunShellScript --comment \'Demo run shell script on Linux Instances\' --parameters \'{"commands":["#!/usr/bin/python","print \"Hello world from python\""]}\' --output text --query \'Command.CommandId\''.format(instance_id))
    # os.system('aws ssm send-command --instance-ids {} --document-name AWS-RunShellScript --comment \'Demo run shell script on Linux Instances\' --parameters \'{"commands":["#!/usr/bin/python","print \"Hello world from python\""]}\' --output text --query \'Command.CommandId\''.format(instance_id))
    # os.system('aws ssm send-command --instance-ids {} --document-name {} --comment "Demo run shell script on Linux Instances" --parameters "{"commands":["#!/usr/bin/python","print \"Hello world from python\""]}" --output text --query "Command.CommandId"'.format(instance_id,document_name))
    # os.system('sh_command_id=$(aws ssm send-command --instance-ids {} --document-name {} --comment "Demo run shell script on Linux Instances" --parameters "{"commands":["#!/usr/bin/python","print \"Hello world from python\""]}" --output text --query "Command.CommandId)"')
    # os.system('sh -c "aws ssm list-command-invocations --command-id "{}" --details --query "CommandInvocations[].CommandPlugins[].{Status:Status,Output:Output}"" > output.json')
    # os.system("echo sh_command_id")
# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #


# response = ec2.describe_instance_status(
#     InstanceIds=[
#         'i-0992ee1f06a6ca2af',
#     ],
#     DryRun=False,
#     IncludeAllInstances=True|False
# )

# print(json.dumps(response))



# response = client.send_command(
#         InstanceIds=[
#             "",
#         ],
#         DocumentName='AWS-RunShellScript',
#         TimeoutSeconds=123,
#         Comment='Demo run shell script on Linux Instances',
#         Parameters={
#             'commands': [
#                 '#!/usr/bin/python',
#                 "print \"Hello world from python\""
#             ]
#         }
#     )
# print(response)


response = client.list_command_invocations(
    MaxResults=50,
    Details=True|False
)

print(response)

# terminateInstances()
# print("Instances ended.")
# endInstances()
# runInstances(1)
# print("Instances ran.")
# print(ec2.describe_instances())
# waitAndSend()
# print("Files Sent.")
# sendFile()
# wait()
# os.system('python find_nonce.py 0 100 3')