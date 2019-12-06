import hashlib
import time
import sys
import os
import logging

# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #
challenger_string = "COMSM0010cloud"
pure_zeros = True
scale = 16  # equals to hexadecimal
num_of_bits = 256  # number of bits to output from hex
# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #

def find_nonce(difficulty, time_limit, instance_number, VMS, log):

    i = instance_number

    finished = False
    mytime = time.time()
    while(not finished):
        if (log == True):
            logging.debug(str(i))
        if(time.time() - mytime > time_limit):
            break

        proof = "{0:b}".format(i)
        block = challenger_string + proof
        result = hashlib.sha256(block.encode('utf-8')).hexdigest()
        result = hashlib.sha256(block.encode('utf-8')).hexdigest()
        result_binary = bin(int(result, scale))[2:].zfill(num_of_bits)

        if (result_binary[:difficulty] == '0' * difficulty):
            print("Nonce found:")
            print(block)
            return (block)
        if (i >= 2**32):
            break
        i+=VMS

if (__name__ == "__main__"):
    instance_number = int(sys.argv[1])
    time_limit = float(sys.argv[2])
    difficulty = int(sys.argv[3])
    VMS = float(sys.argv[4])
    VMS = int(VMS)
    log = bool(sys.argv[5])
    start = time.time()  # countdown
    result = find_nonce(difficulty, time_limit, instance_number, VMS, log)
    time = str(time.time() - start) + "s"
    if (result == None):
        print("No nonce found")
        print(time)
    else:
        print(time)
