import os
import sys

if (__name__ == "__main__"):
    instance_id = str(sys.argv[1])
    os.system("aws ec2 terminate-instances --instance-ids {} --region eu-west-2".format(instance_id))