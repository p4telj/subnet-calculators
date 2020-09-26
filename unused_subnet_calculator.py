"""
unused_subnet_calculator.py

Calculates unused subnets given an address space and allocated subnets.
"""

import itertools
import argparse
import sys

from classes import IP, IPRange, CIDR

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

# initialize existing network
try:
    print("Analyzing existing network...", end=" ")
    network_cidr = CIDR(cidr_string=args.network)
    print("Done.\n")
    network_cidr.print_summary()
    
    print("Validating allocated subnets...", end=" ")
    subnets = []
    # create CIDR objects per input
    for cidr_string in args.allocated:
        # verify that each CIDR exists within the larger network
        subnets.append(CIDR(cidr_string=cidr_string))
        if not subnets[-1].is_within(network_cidr):
            raise ValueError(f"Allocated subnet CIDR {subnets[-1]} is not within network.")
    # Verify that each of the subnets do not overlap with each other.
    for i, subnet in enumerate(subnets):
        for j, other in enumerate(subnets):
            if i != j and subnet.does_overlap(other):
                raise ValueError(f"Allocated subnets {subnet} and {other} overlap.")
    print("Done.")
    
    print("Calculating unused subnet CIDRs...", end=" \n")
    # create IPRange of network to use the start/end
    network_range = IPRange(cidr=network_cidr)
    # create a list of all IPRanges in network and sort it
    subnet_ranges = sorted([IPRange(cidr=subnet_cidr) for subnet_cidr in subnets])
    # create a list of all IPs in network
    ips = [network_range.range[0]] # start of network
    for ipr in subnet_ranges:
        ips.append(ipr.range[0])
        ips.append(ipr.range[1])
    ips.append(network_range.range[1]) # end of network
    # [print(ip) for ip in ips]
    # create IPRange of all the gaps in the network
    # if indices [0, 1] and [-2, -1] are equivalent IPs (network boundary), eliminate from list
    # since all the subnet cidrs don't overlap, we can exclude altogether
    # also, except for network boundaries, all the ranges should exclude the IPs
    # which is why each one will have 1 host added or subtract unless network boundary
    unused_ranges = []
    for fip, sip in zip(*[iter(ips)]*2):
        # fip == sip on border is possible
        # fip + 1 == sip is possible in between subnets
        if fip == sip or IP.if_add_hosts(fip, 1) == sip:
            continue
        fip.add_hosts(0 if fip == ips[0] else 1)
        # print(fip == ips[0])
        sip.remove_hosts(0 if sip == ips[-1] else 1)
        # print(sip == ips[-1])
        unused_ranges.append(IPRange(first_ip=fip, second_ip=sip))
        # print(fip)
        # print(sip)
        # print()
    [print(x) for x in unused_ranges]
    unused_cidrs = [CIDR.from_ip_range(ipr) for ipr in unused_ranges]
    unused_cidrs = list(itertools.chain.from_iterable(unused_cidrs))
    print("Done.\n")
    [print(u) for u in unused_cidrs]
except Exception as e:
    print(f"ERROR => {str(e)}")
    sys.exit(1)
