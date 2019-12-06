import boto3
from botocore.exceptions import ClientError
import os
import json
import time
import sys
import math
import signal
import argparse
import csv

# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #
ec2 = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
client = boto3.client('ssm')
AMI_ID = "ami-04de2b60dd25fbb2e"
no_of_instances = 1
DNS_name = []
iam_role_name = "EnablesEC2ToAccessSystemsManagerRole"

parser = argparse.ArgumentParser(
    description="Run blockchain with difficulty D",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--log",
    default=False,
    help="If we should log files in python script",
)

parser.add_argument(
    "--difficulty",
    default=1,
    type=int,
    help="Difficulty of nonce discovery",
)

parser.add_argument(
    "--time-limit",
    default=1,
    type=float,
    help="Maximum time blockchain will run for in ms",
)

parser.add_argument(
    "--vms",
    default=1,
    type=int,
    help="Number of virtual machines to spawn",
)

parser.add_argument(
    "--confidence",
    default=1,
    type=float,
    help="Confidence value",
)
# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #

# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #
def sendFile(dns):
    os.system("scp -i MyFirstKey.pem -o 'StrictHostKeyChecking no' brute_find_nonce.py ec2-user@{}:~".format(dns))
    
def runInstances(i):
    os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --iam-instance-profile Name={} --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" > stop-output.json'.format(iam_role_name, i))

def queryInstances():
    os.system("aws ec2 describe-instances --output json > instances-raw.json")

def waitAndSend(difficulty, VMS, time_limit, logging):
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress,PublicDnsName]' --output json > instances.json")
    f = open("instances.json","r")
    instances = json.load(f)
    iterator = 0

    for i in instances:
        for instance_id in i:

            instance = instance_id[0]
            dns = instance_id[5]
            state = instance_id[1]

            if (not(state['Name'] == 'terminated' or state['Name'] == 'shutting-down')):
                DNS_name.append(dns)
                wait(instance, 'eu-west-2') #wait until instance is running
                sendFile(dns) #this takes dns
                print("Files Sent.")
                runFile(instance, "AWS-RunShellScript", difficulty, time_limit, iterator, VMS, logging)
                iterator +=1

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
    os.system("ssh -i MyFirstKey.pem ec2-user@{}:~".format(dns))

def emergencyStop(signum, frame):
    print("Emergency stop")
    print(frame)

    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress,PublicDnsName]' --output json > instances.json")
    f = open("instances.json","r")
    instances = json.load(f)

    for i in instances:
        for instance_id in i:

            instance = instance_id[0]
            dns = instance_id[5]
            state = instance_id[1]

            if (not(state['Name'] == 'terminated' or state['Name'] == 'shutting-down')):
                response = client.send_command(
                    InstanceIds=[
                        str(instance),
                    ],
                    DocumentName="AWS-RunShellScript",
                    TimeoutSeconds=60000,
                    Comment='Get log files from find_nonce.py',
                    Parameters={
                        'commands': [
                            'cat /var/log/cloud-init-output.log'
                        ]
                    }
                )

                commandId = response["Command"]["CommandId"]

                acknowledged = False

                while (not acknowledged):
                    response_r = client.list_command_invocations(
                        CommandId = str(commandId),
                        InstanceId = instance,
                        Details=True
                    )
                
                    commandInvocations = response_r["CommandInvocations"]
                    
                    if (commandInvocations):
                        output = response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"]
                        resp = commandInvocations[0]["Status"]
                        if (resp == "Success"):
                            acknowledged = True
                            print("Response: {}".format(resp))
                            print("Output: {}".format(output))
                        elif(resp == "Failed"):
                            print("Command Failed")
                        elif (resp == "TimedOut"):
                            print(output)

                time.sleep(5) #checking every 5 seconds to not exceed API call limit

    terminateInstances()
    exit()

def terminateVM(instance_id):
    ec2.terminate_instances(InstanceIds=[instance_id], DryRun=False)
    updateInstances()
    print("Instance {} terminated.".format(instance_id))

def terminateInstances():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress]' --output json > instances.json")
    #loop through and terminate all instances
    f = open("instances.json","r")
    instances = json.load(f)
    for i in instances:
        for info in i:
            instance_id = info[0]
            try:
                ec2.terminate_instances(InstanceIds=[instance_id], DryRun=False)
            except ClientError as e:
                print(e)
    updateInstances()
    print("Instances terminated")

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
                IncludeAllInstances=True
        )

        if (instance.state['Name'] == 'running' and ((response['InstanceStatuses'][0]["SystemStatus"]["Status"]) == "ok") and (response['InstanceStatuses'][0]["InstanceStatus"]["Status"] == "ok")):
            not_initialised = False
            print("Instance {} up and running!".format(instance_id))
            break
            # print(json.dumps(response))
        # else:
        #     print(instance.state['Name'])

def createSSMCommand():
    os.system("aws ssm create-document --content file:///home/ec2-user/RunShellScript.json  --name `RunShellScript` --document-type `Command`")

def authoriseSecurityGroup(sg, port, ip):
    port = 22
    os.system("aws ec2 authorize-security-group-ingress --group-id {} --protocol tcp --port {} --cidr {}",format(sg,port, ip))


def runFile(instance_id, document_name, difficulty, time_limit, instance_number, VMS, logging):

    client.send_command(
        InstanceIds=[
            str(instance_id),
        ],
        DocumentName=document_name,
        TimeoutSeconds=60000,
        Comment='Try and Run find_nonce.py',
        Parameters={
            'commands': [
                'python /home/ec2-user/brute_find_nonce.py {} {} {} {} {}'.format(instance_number, time_limit, difficulty, VMS, logging)
            ]
        }
    )

def checkEnding(VMS):
    if (VMS == 15):
        terminateInstances()

def checkResults(totalVMS):
    print("Waiting for results...")

    ec2Finished = False
    checkingFastest = False
    terminatedVMS = 0
    while not ec2Finished:
        instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            instance = str(instance.id)
            response_r = client.list_command_invocations(
                InstanceId=instance,
                Details=True
            )    

            commandInvocations = response_r["CommandInvocations"]
            
            if (commandInvocations):
                # print(commandInvocations[0]["Status"])
                output = response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"]
                resp = commandInvocations[0]["Status"]
                if (resp == "Success"):
                    
                    #if one VM has finished and found none, terminate and continue others
                    if (output[:14] == "No nonce found" and (terminatedVMS <= totalVMS)):
                        print("VM {} did not find a nonce".format(instance))
                        terminateVM(instance) #Terminate the VM
                        terminatedVMS+=1
                        if (terminatedVMS == totalVMS):
                            ec2Finished = True
                            checkEnding(totalVMS)
                    #we found a nonce
                    elif(output[:11] == "Nonce found"):
                        terminateInstances()
                        terminatedVMS = totalVMS
                        ec2Finished = True
                        checkEnding(totalVMS)
                        print(response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"])
                        break
                # If the command failed
                elif(resp == "Failed"):
                    print("Command Failed")
                    print(response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"])
                    terminatedVMS +=1
                    if (terminatedVMS == totalVMS): 
                        ec2Finished = True #if this is the last VM, exit the loop
                        checkEnding(totalVMS)
                    terminateVM(instance) #Terminate the VM
                    break
                elif (resp == "TimedOut"):
                    print(output)
                    terminatedVMS+=1
                    if (terminatedVMS == totalVMS): 
                        ec2Finished = True #if this is the last VM, exit the loop
                        emergencyStop(1,1)
                    terminateVM(instance) #Terminate the VM
                    break
        time.sleep(5) #checking every 5 seconds to not exceed API call limit

    if(checkingFastest):
        instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

        for instance in instances:
            
            acknowledged = False
            
            while (not acknowledged):

                response_r = client.list_command_invocations(
                    InstanceId=instance.id,
                    Details=True
                )

                commandInvocations = response_r["CommandInvocations"]
                
                if (commandInvocations):
                    output = response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"]
                    print(output)
                    acknowledged = True


def updateInstances():
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress,PublicDnsName]' --output json > instances.json")
    # instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    
    # print(instances)

    # os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State,Name,LaunchTime,PublicIpAddress,PublicDnsName]' --output json > instances.json")
    # instances  = json.load(open("instances.json"))
    # index = 0
    # for i in instances:
        # j = i[0]
        # print(j)
        # if not(j[5]):
            # print(instances[index])
            # instances.pop(index)
            # index+=1
        # else:
            # print("hi")
            # print(instances[index])
            # print("hi")
            # index = 0

    # print(instances)

    # with open('instances.json', 'w') as outfile:
        # json.dump(instances, outfile)


# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #



# ------------------------------------------------------------- COMMANDS ------------------------------------------------------------- #
if (__name__ == "__main__"):
    args = parser.parse_args()
    if (args.log == True):
        logging = True
        print("Logging")
    else:
        logging = False
    if (args.vms):
        VMS = args.vms
    if (args.time_limit):
        time_limit = args.time_limit * 60
    if (args.difficulty):
        difficulty = args.difficulty
    if (args.confidence):
        confidence = args.confidence

    signal.signal(signal.SIGINT, emergencyStop)

    y_intercept = -19

    exp_time = 2**(difficulty + y_intercept)

    lambdaa = -math.log(1 - confidence)

    max_time = lambdaa * exp_time #run time to guarantee confidence interval

    index = 1
    foundVM = False

    # with open('times.csv', 'r') as csv_file:
    #     csv_reader = csv.reader(csv_file)
    #     for row in csv_reader:
    #         if (not("difficulty" == row[0])):
    #             if (int(row[0]) == difficulty):
    #                 for item in row:
    #                     if (item[-2:] == "ms"):
    #                         rec_time = int(item[:len(item)-2])
    #                         if (max_time >= rec_time):
    #                             foundVM = True
    #                             VMS = index
    #                             break
    #                         else:
    #                             if(index == 1):
    #                                 index = 0
    #                                 index += 2

    if (foundVM == False):
        VMS = 15

    VMS = math.ceil(max_time / time_limit)

    if (args.vms):
        if (args.vms > 1):
            VMS = args.vms

    VMS = int(VMS)

    print(max_time, time_limit, difficulty, confidence, VMS, logging)

    terminateInstances()
    runInstances(VMS)
    waitAndSend(difficulty, VMS, time_limit, logging)
    print("Instances queued.")
    checkResults(VMS)
    
# ------------------------------------------------------------- COMMANDS ------------------------------------------------------------- #