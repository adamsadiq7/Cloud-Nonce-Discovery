import hashlib
import time
  
challenger_string = "COMSM0010cloud"
pure_zeros = True
# challenger_string = ' '.join(map(bin,bytearray(original_challenger_string,'utf8')))

scale = 16 ## equals to hexadecimal
num_of_bits = 256
number_of_zeros = 0

# def hexToBinary(hex_d):
#     binary = hex(hex_d))
#     for i in range (0,4):
#         if
#         number_of_zeros+=1

def find_nonce(start, end, difficulty):
    for i in range(start, end):
        pure_zeros = True
        nonce_found = False
        proof = "{0:b}".format(i) #no need to do this
        # print(proof)
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
                    # print(result_binary) #printing value
                    break
            j += 1
        if (nonce_found):
            break

        # if result_binary[0:difficulty] & 111111111111111


iterations = input("iterations:")
difficulty = input("difficulty:")

start = time.time() # countdown

find_nonce(0, iterations, difficulty)
print(str(time.time() - start) + "s")