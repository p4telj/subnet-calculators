"""
IP.py

Contains class definition.
"""

import copy


class IP:
    """Represents an IPv4 address."""
    OCTETS = 4
    BITS_PER_OCTET = 8
    
    OCTET_RANGE = 256
    MAX_OCTET_NUM = 255
    MIN_OCTET_NUM = 0

    OCTET_POWERS = [
        1, # 256**0
        256, # 256**1
        65536, # 256**2
        16777216 # 256**3
    ]

    def __init__(self, *, ip_string=None, ip_list=None):
        """
        Constructor: Converts IP string into octet list.
        
        (1) Create an IP given a string (EX) 10.0.0.0

        or

        (2) Create an IP given a list (EX) [10, 0, 0, 0]
        """
        if type(ip_string) == str:
            try:
                # each octet must be parse-able as an integer
                self.ip = [int(ip) for ip in ip_string.split(".")]
            except:
                # propagate error to client
                raise ValueError(f"{ip_string}: incorrect ip_string input to IP: " +
                    "octets must be integers <= 255 and >= 0. EX: 255.125.221.0")
        elif type(ip_list) == list:
            for ip in ip_list:
                if not type(ip) == int:
                    raise ValueError(f"{ip_list}: incorrect ip_list input to IP: " +
                        "Must be a list of numbers (EX: [10, 0, 0, 0])")
            # avoid any issues with references
            self.ip = copy.deepcopy(ip_list)
        else:
            raise ValueError("IP input must be either (string) ip_string (EX: 10.0.0.0) or " +
                "(list) ip_list (EX. [10,0,0,0])")
        # validate IP
        self._validate()
        # if valid, creates a numerical representation of IP
        self.ip_num = self._to_numerical()
        return

    def _validate(self):
        """Validates IP."""
        if len(self.ip) != IP.OCTETS:
            raise ValueError(f"{self}: octet count must be {IP.OCTETS}. EX: 255.255.255.255")
        if self.ip[0] == 0:
            raise ValueError(f"{self}: first octet cannot be 0 as it is reserved.")
        for octet in self.ip:
            if octet < IP.MIN_OCTET_NUM or octet > IP.MAX_OCTET_NUM:
                raise ValueError(f"{self}: octets must be integers <= {IP.MAX_OCTET_NUM} " + 
                                 f"and >= {IP.MIN_OCTET_NUM}. EX: 255.125.221.0")
        return

    def _to_numerical(self):
        """# of hosts between IP and 0.0.0.0"""
        total = 0
        for i in range(len(self.ip)):
            # OCTET_POWERS[i] = 256**[i] pre-calculated
            # essentially converts IP bits into an integer one octet at a time (i)
            # as the octet becomes more "significant", it increases addresses by
            # a magnitude of 256 (IP.OCTET_RANGE)
            total += self.ip[i] * IP.OCTET_POWERS[abs(i - IP.OCTETS + 1)]
        return total

    def _from_numerical(self, num):
        """
        From # of hosts between IP and 0.0.0.0 to an IP address.
        """
        ip = []
        left = num
        for i in range(len(self.ip)):
            # OCTET_POWERS[i] = 256**[i] pre-calculated
            # uses the fact that a more "significant" octet increases
            # addresses by a magnitude of 256 (IP.OCTET_RANGE) at a time
            octet_val = IP.OCTET_POWERS[abs(i - IP.OCTETS + 1)]
            ip.append(left // octet_val)
            left -= (ip[-1] * octet_val)
        return ip

    def add_hosts(self, hosts):
        """Increase the IP address by # hosts."""
        self.ip_num += hosts
        self.ip = self._from_numerical(self.ip_num)
        return self

    def remove_hosts(self, hosts):
        """Decrease the IP address by # hosts."""
        self.ip_num -= hosts
        self.ip = self._from_numerical(self.ip_num)
        return self

    def is_adjacent(self, other):
        """If IP address is adjacent to another IP address."""
        return abs(self.ip_num - other.ip_num) == 1

    def __str__(self):
        """String representation."""
        return ".".join([str(ip) for ip in self.ip])

    def __sub__(self, other):
        """
        Subtraction override that represents the # of hosts between inclusive IPs.
        Once again, this is an inclusive range, hence the +1
        """
        return abs(self.ip_num - other.ip_num) + 1

    def __eq__(self, other):
        """== comparator."""
        for i, ip in enumerate(self.ip):
            if ip != other.ip[i]:
                return False
        return True

    def __ne__(self, other):
        """!= comparator."""
        return not self.__eq__(other)

    def __lt__(self, other):
        """< comparator."""
        for i, ip in enumerate(self.ip):
            if ip < other.ip[i]:
                return True
            if ip > other.ip[i]:
                return False
        return False

    def __le__(self, other):
        """<= comparator."""
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other):
        """> comparator."""
        return not self.__le__(other)

    def __ge__(self, other):
        """>= comparator."""
        return not self.__lt__(other)

    def __getitem__(self, index):
        """[] override."""
        return self.ip[index]
