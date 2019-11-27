import hashlib
import time
import sys
import os
import logging

logging.basicConfig(filename="log.log", level= logging.DEBUG)

# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #
challenger_string = "COMSM0010cloud"
pure_zeros = True
scale = 16  # equals to hexadecimal
num_of_bits = 256  # number of bits to output from hex
# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #


def find_nonce(difficulty, time_limit, instance_number):
    instructionsPerS = 187248
    ec2_range = instructionsPerS * time_limit

    start = instance_number * ec2_range
    end = (instance_number + 1) * ec2_range
    my_start = time.time()
    for i in xrange(start, end):
        logging.debug(str(i))
        if (time.time() - my_start > time_limit):
            break

        proof = "{0:b}".format(i)
        block = proof + challenger_string
        result = hashlib.sha256(block.encode('utf-8')).hexdigest()
        result_binary = bin(int(result, scale))[2:].zfill(num_of_bits)

        if (result_binary[:difficulty] == '0' * difficulty):
            print("Nonce found:")
            print(block)
            return (block)


if (__name__ == "__main__"):
    start = time.time()  # countdown
    instance_number = int(sys.argv[1])
    difficulty = int(sys.argv[2])
    time_limit = int(sys.argv[3])
    result = find_nonce(difficulty, time_limit, instance_number)
    time = str(time.time() - start) + "s"
    if (result == None):
        print("No nonce found")
        print(time)
    else:
        print(time)