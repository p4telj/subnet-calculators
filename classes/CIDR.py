"""
CIDR.py

Contains class definition.
"""

import math
import copy

from classes import IP, IPRange


class CIDR:
    """Represents an IPv4 CIDR Block."""
    max_mask = 32
    min_mask = 0

    def __init__(self, *, cidr_string=None, ip=None, mask=None):
        """
        Constructor.
        
        (1) Converts CIDR block string into base IP, mask, and IP Range
        or
        (2) Converts IP Range into CIDR Block string, base IP, and mask.
        """
        if type(cidr_string) == str:
            # fill in mask value & validate
            split = []
            try:
                split = cidr_string.split("/")
                # must be split into IP/mask
                if (len(split) != 2):
                    raise ValueError("CIDR string is incorrectly formatted.")
                # mask must be parse-able as an integer
                self.mask = int(split[1])
                # mask must fit into range
                if self.mask < CIDR.min_mask or self.mask > CIDR.max_mask:
                    raise ValueError("Mask out of range.")
            except:
                # propagate error to client
                raise ValueError(f"{cidr_string}: format is IP/mask, EX. 10.0.0.0/5, where mask <= 32 and >= 0")

            # create an IP object
            self.base_ip = IP(ip_string=split[0])
            # string representation
            self.cidr_string = cidr_string
        elif isinstance(ip, IP) and type(mask) == int:
            self.mask = mask
            # mask must fit into range
            if self.mask < CIDR.min_mask or self.mask > CIDR.max_mask:
                raise ValueError(f"Mask {self.mask} out of range.")
            # references IP object
            self.base_ip = copy.deepcopy(ip)
            # string representation
            self.cidr_string = f"{str(self.base_ip)}/{str(self.mask)}"
        else:
            raise ValueError("CIDR input must be either cidr_string or ip and mask.")
        # calculate total hosts
        self.hosts = CIDR.get_hosts(self.mask)
        # IP range representation
        self.cidr_range = IPRange(cidr=self)
        return

    def __str__(self):
        """String representation."""
        return self.cidr_string

    def print_summary(self):
        """Prints summary."""
        print(f"CIDR Notation: {self.cidr_string}")
        print(f"IP Mask: {self.mask}")
        print(f"IP Range: {self.cidr_range}")
        print(f"Total Hosts: {self.hosts}")
        print("")
        return

    @classmethod
    def get_hosts(cls, mask):
        """Gets hosts using CIDR mask."""
        return 2**(cls.max_mask-mask)

    def is_within(self, other):
        """Determines if current CIDR is within other CIDR."""
        return self.cidr_range.is_within(other.cidr_range)

    def does_overlap(self, other):
        """Determines if current CIDR overlaps with other CIDR."""
        return self.cidr_range.does_overlap(other.cidr_range)

    @classmethod
    def from_ip_range(cls, ip_range):
        """
        Converts an IP Range to a list of CIDR objects that match.
        
        The reason this isn't in the constructor is that it returns a list of CIDRs.
        """
        ip_range_copy = copy.deepcopy(ip_range) # will be modifying, so don't want to touch ref
        # print(f"range: {ip_range_copy}\n")
        ipr = ip_range_copy.range
        hosts = ip_range_copy.hosts
        cidrs = []
        # # start cutting down the number of hosts by using masks
        # next_ip = ipr[0]
        # while hosts:
        #     mask = CIDR.max_mask - math.floor(math.log(hosts, 2))
        #     # covered_hosts = CIDR.get_hosts(mask)
        #     # print(f"hosts left to cover: {hosts}")
        #     # print(f"covered hosts: {covered_hosts}")
        #     # hosts -= covered_hosts # these are the hosts left to cover
        #     # print(f"updated hosts left to cover: {hosts}")
        #     cidrs.append(CIDR(ip=next_ip, mask=mask))
        #     covered_hosts = cidrs[-1].cidr_range.hosts
        #     print(f"hosts left to cover: {hosts}")
        #     print(f"covered hosts: {covered_hosts}")
        #     hosts -= covered_hosts
        #     print(f"updated hosts left to cover: {hosts}")
        #     print(f"cidr: {cidrs[-1]}")
        #     print(f"cidr to IPRange: {cidrs[-1].cidr_range}")
        #     print(f"ip before adding hosts: {next_ip}")
        #     # next_ip = copy.deepcopy(cidrs[-1].cidr_range.range[-1]).add_hosts(1)
        #     next_ip.add_hosts(covered_hosts) # +1 before
        #     print(f"ip after adding hosts: {next_ip}")
        #     print()
        start_ip = ipr[0]
        end_ip = ipr[1]
        while (start_ip <= end_ip):
            # mask that covers remaining hosts
            mask_for_hosts = CIDR.max_mask - math.floor(math.log(hosts, 2))
            # https://stackoverflow.com/questions/33443914/how-to-convert-ip-address-range-to-cidr-in-java
            # mask that marks the location of first 1's from lower bit to higher bit of start IP
            # the reason is we want to avoid exceeding the maximum IP with a mask too big
            # when we say "maximum_mask" we mean the smallest it can be, since smaller mask covers more
            maximum_mask = CIDR.max_mask - math.floor(math.log(start_ip._to_numerical() & (-start_ip._to_numerical()), 2))
            mask = max(mask_for_hosts, maximum_mask)
            cidrs.append(CIDR(ip=start_ip, mask=mask))
            hosts_covered = CIDR.get_hosts(mask)
            hosts -= hosts_covered
            start_ip.add_hosts(hosts_covered)
        return cidrs
