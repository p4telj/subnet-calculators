"""
CIDR.py

Contains class definition.
"""

import math
import copy

from networking import IP, IPRange


class CIDR:
    """Represents an IPv4 CIDR Block."""
    MAX_MASK = 32
    MIN_MASK = 0

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
                if self.mask < CIDR.MIN_MASK or self.mask > CIDR.MAX_MASK:
                    raise ValueError(f"Mask {self.mask} out of range.")
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
            if self.mask < CIDR.MIN_MASK or self.mask > CIDR.MAX_MASK:
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

    def print_summary(self):
        """Prints summary."""
        print(f"CIDR Notation: {self.cidr_string}")
        print(f"IP Mask: {self.mask}")
        print(f"IP Range: {self.cidr_range}")
        print(f"Total Hosts: {self.hosts}\n")
        return

    def is_within(self, other):
        """Determines if current CIDR is within other CIDR."""
        return self.cidr_range.is_within(other.cidr_range)

    def does_overlap(self, other):
        """Determines if current CIDR overlaps with other CIDR."""
        return self.cidr_range.does_overlap(other.cidr_range)

    @classmethod
    def get_hosts(cls, mask):
        """Gets hosts using CIDR mask."""
        return 2**(cls.MAX_MASK - mask)

    @classmethod
    def from_ip_range(cls, ip_range):
        """
        Converts an IP Range to a list of CIDR objects that match.
        
        The reason this isn't in the constructor is that it returns a list of CIDRs.
        """
        ip_range_copy = copy.deepcopy(ip_range) # will be modifying, so don't want to touch ref
        ipr = ip_range_copy.range
        hosts = ip_range_copy.hosts

        cidrs = []
        start_ip = ipr[0]
        end_ip = ipr[1]
        # creating CIDRs using start_ip and trying to determine a mask that covers
        # as many IP addresses as possible without overshooting.
        # "mask_for_hosts" attempts to look at remaining hosts and find a matching mask.
        # however, it can overshoot, which is why "restricted_mask" is calculated.
        # the max is taken (the larger the mask, the less IPs covered)
        # and the IP is incremented by the # of hosts that are covered. 
        while (start_ip <= end_ip):
            # mask that covers remaining hosts
            mask_for_hosts = CIDR.MAX_MASK - math.floor(math.log(hosts, 2))
            # https://stackoverflow.com/questions/33443914/how-to-convert-ip-address-range-to-cidr-in-java
            # mask that first marks the location of first 1 from lower bit to higher bit of start IP.
            # then, a log_2 is calculated over that value so determine the # of bits for the mask.
            # this is calculated to avoid the mask covering IPs that we don't want.
            restricted_mask = CIDR.MAX_MASK - math.floor(math.log(start_ip._to_numerical() & (-start_ip._to_numerical()), 2))
            # take the max of the masks, using the most restricted mask
            mask = max(mask_for_hosts, restricted_mask)
            # append a CIDR using the start_ip and the calculated mask
            cidrs.append(CIDR(ip=start_ip, mask=mask))
            # host computation
            hosts_covered = CIDR.get_hosts(mask)
            hosts -= hosts_covered
            # increment start_ip with hosts covered by the mask
            start_ip.add_hosts(hosts_covered)
        return cidrs

    def __str__(self):
        """String representation."""
        return self.cidr_string
