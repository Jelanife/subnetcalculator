'''
    This program calculates information about a subdivided network address space.

    The user is prompted for a slash notation IPv4 network address and the 
    desired number of subnets to divide that netork into.  If subdivision is
    possible giving the user inputs, the program will output the following 
    ingformation about the 1st and last NUM_RESULTS subnets:
    1) Desired subnets
    2) Actual subnets
    3) Host per subnet
    4) Total number of hosts in the divided address space
    5) Tab delimited table with following fields:
        1) Subnet number (starting at 1)
        2) Subnet address in slash notation
        3) First usable address
        4) Last usable address
        5) Broadcast address

    Supply command line arguments to skip the runtime prompts
    1) Slash notation network address
    2) Desired subnets
    3) -n NUM_RESULTS VALUE *
    4) -s This flag will cause only the tab delimited field entries to print *

    * Theses options are only available if arguments 1 and 2 are supplies as well.
      Using them with 1 and 2 will cause the program to crash or exit.

    Examples:
    1) Divide a Class A address into 32 subnets
        python subnetcalc.py 25.0.0.0/8 32
    2) Divide a Class B address into 64 subnets and print the first and last subnet
        python subnetcalc.py 172.16.0.0/16 64 -n 1
    3) divide a Class A address into 32 subnets, print all subnets, but only the table
        python subnetcalc.py 192.168.0.0/24 32 -n -1 -s


    Jelani Felix 2023
'''


import sys

# default number of results to print
# set to -1 to print all subnets
NUM_RESULTS = 10

# Set to True to print only the subnet info table
JUST_RESULTS = False

# Convert a 32-bit integer into a string of dotted decimal octets
def int_to_dotted_decimal(n):
    res = ""
    for i in range(3):
        octet = n & 0xff
        res = "." + str(octet) + res
        n = n >> 8
    res = str(n) + res
    return res

# Convert an integer representing mask width into an integer mask
def get_int_mask(width):
    mask = 0
    for i in range(width):
        mask = mask | (1 << i)
    mask = mask << (32 - width)
    return mask


if len(sys.argv) == 1:
    #get input from the user
    network_address_with_prefix = input("Enter starting network ID"\
                                        " and prefix in slash notation: ")
    desired_subnets = int(input("Enter the desired number of subnets: "))
else:
    #parse command line inputs
    network_address_with_prefix = sys.argv.pop(1)
    desired_subnets = int(sys.argv.pop(1))
    while len(sys.argv) > 1:
        flag = sys.argv.pop(1)
        if flag == '-n':
            NUM_RESULTS = int(sys.argv.pop(1))
        elif flag == '-s':
            JUST_RESULTS = True
        else:
            print("bad flag or argument!")
            exit(1)
    

#compute the actual number of subnet and the subnet ID width
num_subnets = 1
subnet_id_width = 0

while num_subnets < desired_subnets:
    num_subnets *= 2
    subnet_id_width += 1


#extract the width of the network mask provided as input
network_mask_width = int(network_address_with_prefix.split('/')[1])

# convert the dotted decimal network address into an integer
network_address_str = network_address_with_prefix.split('/')[0]
network_address = 0
octets = network_address_str.split('.')

for i in range(4):
    network_address |= int(octets[i]) << (8*(3-i))

# compute the new subnet mask
new_subnet_mask_width = network_mask_width + subnet_id_width
new_subnet_mask = get_int_mask(new_subnet_mask_width)

# compute a host ID mask and host ID mask width
host_id_mask = 0xffffffff & ~new_subnet_mask
host_id_width = 32 - subnet_id_width - network_mask_width


# check the network address for bits outside the mask
# warn the user out side bits may cause problems
original_host_mask = 0xffffffff & ~get_int_mask(network_mask_width)
if original_host_mask & network_address != 0:
    print("Input network address contains more bits than the subnet mask.\n"\
          "This may cause errors in the calculation.")
    

# compute the subnets, and important addresses then print the results

# print only if -s flag was set
if not JUST_RESULTS:
    # calculate the number of hosts per subnet
    
    hosts_per_subnet = 2**host_id_width - 2
    print('-'*80)
    print("Divide the network {} into {} subnets."\
        .format(network_address_str, desired_subnets))
    print("Desired Subnets: {}".format(desired_subnets))
    print("Actual Subnets: {}".format(num_subnets))
    print("Hosts per Subnet: {}".format(hosts_per_subnet))
    print("Total Hosts: {}".format(hosts_per_subnet*num_subnets))
    print('-'*80)
    print("Subnet Number\tNetwork Address\tFirst Usable Address"\
        "\tLast Usable Address\tBroadcast Address")
    
current_network_address = network_address & new_subnet_mask    
for subnet_id in range(num_subnets):
    current_network_address = network_address | subnet_id << host_id_width
    
    if subnet_id < NUM_RESULTS or subnet_id >= num_subnets - NUM_RESULTS or NUM_RESULTS == -1:

        broadcast = current_network_address | host_id_mask
        last = broadcast - 1
        first = current_network_address + 1

        current_network_address_str = int_to_dotted_decimal(current_network_address)
        current_network_address_str += '/' + str(new_subnet_mask_width)
        broadcast_str = int_to_dotted_decimal(broadcast)
        last_str = int_to_dotted_decimal(last)
        first_str = int_to_dotted_decimal(first)

        print("{}\t{}\t{}\t{}\t{}".format(\
            subnet_id+1, current_network_address_str,\
                  first_str, last_str, broadcast_str))
    if subnet_id == 10 and NUM_RESULTS != -1:
        print('...\t'*5)
