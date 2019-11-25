import hashlib
import time
import sys
import os

# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #
challenger_string = "COMSM0010cloud"
pure_zeros = True
scale = 16 # equals to hexadecimal
num_of_bits = 256 #number of bits to output from hex
nonce_found = False
# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #

def find_nonce(start, end, difficulty):
    nonce_found = False
    i = 0
    while(not(nonce_found)):
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
                    nonce_found = True
                    print("Nonce found:")
                    print(block)
                    return (block)
            j += 1
        i += 1


if (__name__ == "__main__"):
    start = time.time() #countdown
    start_i = int(sys.argv[1])
    end_i = int(sys.argv[2])
    difficulty = int(sys.argv[3])
    result = find_nonce(start_i, end_i, difficulty)
    time = str(time.time() - start) + "s"
    if (result == None):
        print("No nonce found")
    else:
        print(time)
        # os.system('python home/ec2-user/stop.py {}'.format(instance_id))
else:
    print("Program ran with no arguments!")