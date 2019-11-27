import boto3
from botocore.exceptions import ClientError
import os
import json
import time
import sys

# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #
ec2 = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
client = boto3.client('ssm')
AMI_ID = "ami-04de2b60dd25fbb2e"
no_of_instances = 1
DNS_name = []
iam_role_name = "EnablesEC2ToAccessSystemsManagerRole"


directory = "Documents/University/4th/Cloud\ Computing"
# ------------------------------------------------------------- CONFIG ------------------------------------------------------------- #

# ------------------------------------------------------------ FUNCTIONS ----------------------------------------------------------- #
def sendFile(dns):
    os.system("scp -i ~/{}/MyFirstKey.pem -o 'StrictHostKeyChecking no' ~/{}/find_nonce.py ec2-user@{}:~".format(directory, directory, dns))
    os.system("scp -i ~/{}/MyFirstKey.pem -o 'StrictHostKeyChecking no' ~/{}/test.py ec2-user@{}:~".format(directory, directory, dns))
    
    # os.system("yes")
        # os.system("scp -i MyFirstKey.pem find_nonce.py ubuntu@ec2-{}.compute-1.amazonaws.com:~/data/".format(ip))
    
    # This is working fam.
        # os.system("scp -i ~/Documents/University/4th/Cloud\ Computing/MyFirstKey.pem ~/Documents/University/4th/Cloud\ Computing/find_nonce.py ec2-user@ec2-3-10-169-78.eu-west-2.compute.amazonaws.com:/home/ec2-user")

def runInstances(i):
    os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --iam-instance-profile Name={} --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" > stop-output.json'.format(iam_role_name, i))
    # os.system('aws ec2 run-instances --image-id ami-04de2b60dd25fbb2e --count {} --instance-type t2.micro --key-name MyFirstKey --security-groups "MyFirstSecurityGroup" --user-data://job.sh > output_run.json'.format(i))

def queryInstances():
    os.system("aws ec2 describe-instances --output json > instances-raw.json")

def waitAndSend(time_limit, difficulty):
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
                runFile(instance, "AWS-RunShellScript", time_limit, difficulty, iterator)
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
    os.system("ssh -i /{}/MyFirstKey.pem ec2-user@{}:~".format(directory, dns))

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


def runFile(instance_id, document_name, time_limit, difficulty, instance_number):
    # os.system('aws ssm send-command --instance-ids {} --document-name {} --comment "IP config" --parameters commands=ifconfig --output text'.format(instance_id, document_name))
    # os.system('sh_command_id=$(aws ssm send-command --instance-ids {} --document-name {} --comment "Demo run shell script on Linux Instance" --parameters commands=ls --output text --query "Command.CommandId"'.format(instance_id, document_name))

    # first = "aws ssm send-command --instance-ids {} --document-name AWS-RunShellScript --comment"
    # save this one lad
    # os.system('aws ssm send-command --instance-ids {} --output text --query \'Command.CommandId\' > adam.txt'.format(instance_id))

    instructionsPerS = 187248
    ec2_range = instructionsPerS * time_limit

    start = instance_number * ec2_range
    end = (instance_number + 1) * ec2_range

    print("Running instance {} with start {}, end {}, diff {}, time {}".format(instance_id, start, end, difficulty, time_limit))


    client.send_command(
        InstanceIds=[
            str(instance_id),
        ],
        DocumentName=document_name,
        TimeoutSeconds=60000,
        Comment='Try and Run find_nonce.py',
        Parameters={
            'commands': [
                'python /home/ec2-user/find_nonce.py {} {} {}'.format(instance_number, difficulty, time_limit)
            ]
        }
    )

    # commandId = response["Command"]["CommandId"]


def checkResults(totalVMS):
    print("Waiting for results...")

    ec2Finished = False

    terminatedVMS = 0
    while not ec2Finished:

        instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            instance = str(instance.id)
            response_r = client.list_command_invocations(
                InstanceId=instance,
                Details=True
            )
            time.sleep(15)

            commandInvocations = response_r["CommandInvocations"]
            
            if (commandInvocations):
                print(commandInvocations[0]["Status"])
                output = response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"]
                resp = commandInvocations[0]["Status"]
                if (resp == "Success"):
                    
                    #if one VM has finished and found none, terminate and continue others
                    if (output[:14] == "No nonce found" and (terminatedVMS <= totalVMS)):
                        print("VM {} did not find a nonce".format(instance))
                        terminateVM(instance)
                        terminatedVMS+=1
                        if (terminatedVMS == totalVMS):
                            ec2Finished = True
                    #we found a nonce
                    elif(output[:11] == "Nonce found"):
                        terminateInstances() #terminate all instances
                        terminatedVMS = totalVMS
                        ec2Finished = True
                        print("Instance {} found nonce first".format(instance))
                        print(response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"]) #Output
                        break
                # If the command failed
                elif(resp == "Failed"):
                    print("Command Failed")
                    print(response_r["CommandInvocations"][0]["CommandPlugins"][0]["Output"])
                    terminatedVMS +=1
                    if (terminatedVMS == totalVMS): 
                        ec2Finished = True #if this is the last VM, exit the loop
                    terminateVM(instance) #Terminate the VM
                    break
                elif (resp == "TimedOut"):
                    print(output)
                    terminatedVMS+=1
                    if (terminatedVMS == totalVMS): 
                        ec2Finished = True #if this is the last VM, exit the loop
                    terminateVM(instance) #Terminate the VM
                    break

def terminateVM(instance_id):
    ec2.terminate_instances(InstanceIds=[instance_id], DryRun=False)
    updateInstances()
    print("Instance {} terminated.".format(instance_id))

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
    start = time.time() #countdown
    time_limit = int(sys.argv[1]) * 60
    difficulty = int(sys.argv[2])

    terminateInstances()
    runInstances(10)
    totalVMS = 10
    print("Instances queued.")
    waitAndSend(time_limit, difficulty)
    checkResults(totalVMS)
# ------------------------------------------------------------- COMMANDS ------------------------------------------------------------- #