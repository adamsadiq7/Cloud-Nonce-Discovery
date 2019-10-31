import hashlib
import time
import sys

print("Program is being run")

# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #
challenger_string = "COMSM0010cloud"
pure_zeros = True
scale = 16 # equals to hexadecimal
num_of_bits = 256 #number of bits to output from hex
# -------------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------------- #

def find_nonce(start, end, difficulty):
    for i in range(start, end):
        pure_zeros = True
        nonce_found = False
        proof = "{0:b}".format(i)
        concat = proof + challenger_string
        result = hashlib.sha256(concat.encode('utf-8')).hexdigest()
        result_binary = bin(int(result, scale))[2:].zfill(num_of_bits)

        j = 0
        while (pure_zeros):
            if not(result_binary[j] == '0'):
                pure_zeros = False
            if (j == difficulty - 1):
                if (pure_zeros):
                    nonce_found = True
                    print("Nonce found:")
                    break
            j += 1
        if (nonce_found):
            break
    return (result_binary)


start = time.time() #countdown
if (__name__ == "__main__"):
    start_i = int(sys.argv[1])
    end_i = int(sys.argv[2])
    difficulty = int(sys.argv[3])
    result = find_nonce(start_i, end_i, difficulty)
    time = str(time.time() - start) + "s"
    print(result)
    print(time)
    #stop all instances and return
else:
    print("Program ran with no arguments!")