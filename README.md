# subnet-calculator
This side-project aims to provide access to easy subnet calculations.

It does so by implementing the following classes:
- [Networking/IP](networking/IP.py)
  - This class represents an IPv4 address
- [Networking/IPRange](networking/IPRange.py)
  - This class represents a range of IPv4 addresses using 2 addresses, a start and an end
- [Networking/CIDR](networking/CIDR.py)
  - This class represents an IPv4 CIDR block, which is essentially a range of IP addresses

This project contains the following calculators:
- [Unused Subnet Calculator](unused_subnet_calculator.py)
  - <b>Summary</b>: Given a network CIDR, and allocated subnet CIDRs, calculates unused subnets.
  - <b>Inputs</b>:
    - `-n|--network-cidr` is a CIDR block representing the entire virtual network
    - `-a|--allocated-subnet-list` is a list of CIDRs that have already been allocated for subnets. Conflicts with `-f|--allocated-subnet-file`
    - `-f|--allocated-subnet-file` is a relative filepath containing newline-separated CIDRs that have already been allocated for subnets. Conflicts with `-a|--allocated-subnet-list`
    - `-m|--mask-filter` is an output filter that will return all possible unused subnets with a specific mask (0-32)
  - <b>Outputs</b>:
    - Overview of network (CIDR notation, IP mask, IP range, total hosts)
    - List of all unused subnet CIDRs
    - *(Optional)* List of unused subnet CIDRs that match the mask filter
