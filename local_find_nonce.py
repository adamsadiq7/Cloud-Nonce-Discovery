import hashlib
import time
import sys
import os
import logging
import multiprocessing


logging.basicConfig(filename="log.log", level= logging.DEBUG)

# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #
challenger_string = "COMSM0010cloud"
pure_zeros = True
scale = 16  # equals to hexadecimal
num_of_bits = 256  # number of bits to output from hex
# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #


def find_nonce(difficulty, instance_number, totalInstances):
    
    ec2_range = 2**32 / totalInstances

    start = instance_number * ec2_range
    end = (instance_number + 1) * ec2_range

    my_start = time.time()
    for i in xrange(start, end):

        proof = "{0:b}".format(i)
        block = proof + challenger_string
        result = hashlib.sha256(block.encode('utf-8')).hexdigest()
        result = hashlib.sha256(result.encode('utf-8')).hexdigest()
        result_binary = bin(int(result, scale))[2:].zfill(num_of_bits)

        if (result_binary[:difficulty] == '0' * difficulty):
            print("Nonce found:")
            print(block)
            return (block)


if (__name__ == "__main__"):

    difficulty = int(sys.argv[1])
    
    processes = [ ]
    for i in range(2):
        t = multiprocessing.Process(target=find_nonce, args=(difficulty, i, 2))
        processes.append(t)
        start = time.time()  # countdown
        t.start()

        for one_process in processes:
            one_process.join()
        time = str(time.time() - start) + "s"
        print(time)
        break
