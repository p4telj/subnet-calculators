"""
IPRange.py

Contains class definition.
"""

import copy

from networking import IP


class IPRange:
    """Represents a range of IPv4 addresses."""

    def __init__(self, *, first_ip=None, second_ip=None, cidr=None):
        """
        Constructor.

        (1) Create an IP range given 2 IPs.

        or

        (2) Create an IP range given a CIDR block.
              • Utilizes netmask to determine IP range.
              • E.g. 10.0.0.0/18

              • Netmask = 11111111.11111111.11000000.00000000 = 255.255.192.0
              • Range = 10.0.0.0 to 10.0.63.255
        """
        if cidr is not None:
            try:
                base_ip = cidr.base_ip
                mask = cidr.mask
                hosts = cidr.hosts

                # for each octet in an IP address
                primary_ip_octets = []
                secondary_ip_octets = []
                for i in range(IP.OCTETS):
                    # for each octet, grab <= 8 bits (# bits per octet) from mask to use
                    bits = IP.BITS_PER_OCTET if mask >= IP.BITS_PER_OCTET else mask
                    mask -= bits
                    # bitwise ^ (xor) to calculate netmask segment
                    netmask_octet = IP.MAX_OCTET_NUM ^ ((2**(IP.BITS_PER_OCTET-bits)) - 1)
                    # ip segment bitwise & (and) with netmask segment to calculate primary IP
                    ip_octet = netmask_octet & base_ip[i]
                    primary_ip_octets.append(ip_octet)
                    secondary_ip_octets.append(ip_octet)

                first_ip = IP(ip_list=primary_ip_octets)
                second_ip = IP(ip_list=secondary_ip_octets).add_hosts(cidr.hosts - 1)
                # now, gets evaluated by next "if" statement and gets placed into self.range
            except Exception as e:
                raise ValueError(f"({e}) Incorrect CIDR input to IPRange. Must be a valid instance of type CIDR.")
        if isinstance(first_ip, IP) and isinstance(second_ip, IP):
            # IPRange must be sorted at all times
            if first_ip < second_ip:
                self.range = [copy.deepcopy(first_ip), copy.deepcopy(second_ip)]
            else:
                self.range = [copy.deepcopy(second_ip), copy.deepcopy(first_ip)]
        else:
            raise ValueError("Incorrect IPRange inputs: " +
                "Either pass in first_ip, second_ip of type IP or cidr of type CIDR.")
        # determine # of hosts (inclusive start/end IPs)
        self.hosts = self.range[1] - self.range[0]
        return

    def is_within(self, other):
        """Determines if current IPRange is within other IPRange."""
        return self.range[1] <= other.range[1] if self.range[0] >= other.range[0] else False

    def does_overlap(self, other):
        """Does current IPRange overlap with other IPRange."""
        # internal
        if self.is_within(other):
            return True
        # external
        return not (self.range[1] < other.range[0] or self.range[0] > other.range[1])

    def __str__(self):
        """String representation."""
        return "{} to {}".format(self.range[0], self.range[1])

    def __lt__(self, other):
        """< comparator. Assuming the IPRanges don't overlap."""
        return self.range[1] < other.range[0]

    def __le__(self, other):
        """<= comparator. Assuming the IPRanges don't overlap."""
        return self.range[1] <= other.range[0]

    def __getitem__(self, index):
        """[] override."""
        return self.range[index]
