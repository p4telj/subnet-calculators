"""
unused_subnet_calculator.py

Calculates unused subnets given an address space and allocated subnets.
"""

import itertools
import argparse
import sys

from networking import IP, IPRange, CIDR

# get command line args
parser = argparse.ArgumentParser()
parser.add_argument(
    "-n",
    "--network-cidr",
    help="CIDR representing entire virtual network.",
    dest="network",
    type=str,
    required=True
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-a",
    "--allocated-subnet-list",
    help="List of CIDRs that have already been allocated for subnets. Conflicts with (-f|--allocated-subnet-file)",
    dest="allocated",
    type=str,
    nargs="*"
)
group.add_argument(
    "-f",
    "--allocated-subnet-file",
    help="Relative filepath containing newline-separated CIDRs that have already been allocated for subnets. Conflicts with (-a|--allocated-subnet-list)",
    dest="allocated_file",
    type=str
)
parser.add_argument(
    "-m",
    "--mask-filter",
    help="Output filtering: will return all possible unused subnets with a specific mask (0-32).",
    dest="mask",
    type=int,
    required=False
)
args = parser.parse_args()

try:
    # initialize existing virtual network
    print("Analyzing existing network...", end=" ")
    network_cidr = CIDR(cidr_string=args.network)
    print("Done.\n")
    network_cidr.print_summary()
    
    # validate allocated subnets
    print("Validating allocated subnets...", end=" ")
    allocated = args.allocated
    if allocated is None:
        if args.allocated_file is None:
            raise RuntimeError("No allocated subnets found. Must provide either a file (-f) containing " + 
                               "newline separated subnets, or a list (-a)" )
        # pull file values into a list
        with open(args.allocated_file, "r") as allocated_file:
            allocated = allocated_file.read().splitlines()

    # create CIDR objects per allocated subnets in virtual network
    subnet_cidrs = []
    for cidr_string in allocated:
        # verify that each CIDR exists within the larger network
        subnet_cidrs.append(CIDR(cidr_string=cidr_string))
        if not subnet_cidrs[-1].is_within(network_cidr):
            raise RuntimeError(f"Allocated subnet CIDR {subnet_cidrs[-1]} is not within network.")
    # verify that each of the subnets do not overlap with each other.
    for i, subnet_cidr in enumerate(subnet_cidrs):
        for j, other_subnet_cidr in enumerate(subnet_cidrs):
            if i != j and subnet_cidr.does_overlap(other_subnet_cidr):
                raise RuntimeError(f"Allocated subnets {subnet_cidr} and {other_subnet_cidr} overlap.")
    print("Done.")
    
    print("Calculating unused subnet CIDRs...", end=" ")
    # create IPRange of network to get the start and end IPs
    network_range = IPRange(cidr=network_cidr)
    # create a list of all IPRanges in network and sort it
    subnet_ranges = sorted([IPRange(cidr=subnet_cidr) for subnet_cidr in subnet_cidrs])
    # create a list of all IPs in network
    ips = [network_range.range[0]] # start of network
    for ipr in subnet_ranges:
        ips.append(ipr.range[0])
        ips.append(ipr.range[1])
    ips.append(network_range.range[1]) # end of network

    # from the list of the IPs in the network, create IPRanges that represent
    # the unused ranges of IP addresses.
    # (ex) if network = IPRange(0, 10) & allocated = IPRange(2, 5)
    #      then unused = IPRange(0,1) + IPRange(6,10).
    # rules:
    # (1) network boundaries (in the above example IP(0) and IP(10) are inclusive
    # (2) however, subnet boundaries are exclusive, which is why even if allocated 
    #     IPRange(2,5), we want 0 to 2-1, and then then 5+1 to 10
    unused_ranges = []
    for first_ip, second_ip in zip(*[iter(ips)]*2):
        # fip == sip on border may occur, so we don't want a CIDR to represent that
        # fip + 1 == sip is possible as subnet edges may be next to each other, so no CIDR.
        if first_ip == second_ip or first_ip.is_adjacent(second_ip):
            continue
        unused_ranges.append(
            IPRange(
                first_ip=first_ip.add_hosts(int(first_ip != ips[0])),
                second_ip=second_ip.remove_hosts(int(second_ip != ips[-1]))
            )
        )
    
    # convert each of the IPRanges into a minimum number of CIDR blocks
    # since each call to CIDR.from_ip_range returns a list, we want to condense into 1 list
    unused_cidrs = list(itertools.chain.from_iterable(
        [CIDR.from_ip_range(ipr) for ipr in unused_ranges]
    ))

    print("Done.\n")
    # print results
    [print(u) for u in unused_cidrs]

    # if a specific mask is requested, breaks down the CIDRs from above to reach that
    if args.mask is not None:
        print(f"Filtering/splitting subnets to match mask filter ({args.mask})...", end=" ")

        # validate mask
        CIDR.validate_mask(args.mask)

        # filter out cidrs that have masks > args.mask, since those can't be broken down
        # for cidrs that have masks < args.mask, split them further
        # for cidrs that have masks = args.mask, simply append them
        filtered_cidrs = list(itertools.chain.from_iterable(
            [cidr.divide(args.mask) for cidr in unused_cidrs]
        ))

        print("Done.\n")
        # print results
        [print(f) for f in filtered_cidrs]

except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
