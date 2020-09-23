"""
calculator.py

Calculates unused subnets given an address space and allocated subnets.
"""

import argparse
import sys

# get command line args
parser = argparse.ArgumentParser()
parser.add_argument(
    "-n",
    "--network-cidr",
    help="CIDR representing entire network.",
    dest="network",
    required=True
)
parser.add_argument(
    "-a",
    "--allocated-subnet-cidrs",
    help="CIDRs that have already been allocated for subnets.",
    dest="allocated",
    nargs="*"
)
args = parser.parse_args()

# utility functions
def ipv4_validator(ip):
    """Validates IPv4 Address"""
    split = ip.split(".")
    if len(split) != 4:
        return False
    elif not split[0].isnumeric() or int(split[0]) == 0:
        return False
    for _ip in split:
        if not _ip.isnumeric() or int(_ip) < 0 or int(_ip) > 255:
            return False
    return True

def cidr_validator(cidr):
    """Validates IPv4 CIDR"""
    split = cidr.split("/")
    if len(split) != 2:
        return False
    elif not ipv4_validator(split[0]):
        return False
    elif not split[1].isnumeric() or int(split[1]) < 0 or int(split[1]) > 32:
        return False
    return True

def get_hosts(mask):
    """Gets hosts from CIDR mask"""
    return 2**(32-int(mask))

def is_cidr_within(parent, child):
    """Determines if parent CIDR block contains child CIDR block"""
    return

def do_cidrs_overlap(primary, secondary):
    """Determines if the CIDR blocks overlap"""
    return

def cidr_to_ip_range(cidr):
    """Converts CIDR block to IP range"""
    return

def ip_range_to_cidrs(ip_range):
    """Converts IP range to CIDR blocks that map to it"""
    return


# print out details of existing network
print("Analyzing existing network...\n")
if not cidr_validator(args.network):
    print(f"{args.network} is an invalid network CIDR [-n|--network-cidr]")
    sys.exit(1)

network = {}
network_split = args.network.split("/")
network["cidr"] = args.network
network["block"] = network_split[0]
network["mask"] = network_split[1]
network["hosts"] = get_hosts(network["mask"])

print(f"CIDR Notation: {network['cidr']}")
print(f"IP Block: {network['block']}")
print(f"IP Mask: {network['mask']}")
print(f"Total Hosts: {'{:,}'.format(network['hosts'])}")


# figure out remaining hosts
