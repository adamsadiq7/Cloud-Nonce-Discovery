import hashlib
import time
import sys
import os

# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #
challenger_string = "COMSM0010cloud"
pure_zeros = True
scale = 16 # equals to hexadecimal
num_of_bits = 256 #number of bits to output from hex
# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #

def find_nonce(start, end, difficulty, time_limit):
    my_start = time.time()
    for i in range(start, end):

        if (time.time() - my_start > time_limit):
            break

        # print(time.time() - my_start)

        pure_zeros = True
        proof = "{0:b}".format(i)
        block = proof + challenger_string
        result = hashlib.sha256(block.encode('utf-8')).hexdigest()
        result_binary = bin(int(result, scale))[2:].zfill(num_of_bits)

        j = 0
        while (pure_zeros):
            if not(result_binary[j] == '0'):
                pure_zeros = False
            if (j == difficulty - 1):
                if (pure_zeros):
                    print("Nonce found:")
                    print(block)
                    return (block)
            j += 1



if (__name__ == "__main__"):
    start = time.time() #countdown
    start_i = int(sys.argv[1])
    end_i = int(sys.argv[2])
    difficulty = int(sys.argv[3])
    time_limit = int(sys.argv[4])
    result = find_nonce(start_i, end_i, difficulty, time_limit)
    time = str(time.time() - start) + "s"
    if (result == None):
        print("No nonce found")
        print(time)
    else:
        print(time)
        # os.system('python home/ec2-user/stop.py {}'.format(instance_id))
else:
    print("Program ran with no arguments!")