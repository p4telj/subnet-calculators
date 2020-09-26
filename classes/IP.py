"""
IP.py

Contains class definition.
"""

import copy


class IP:
    """Represents an IPv4 address."""
    max_octet = 255
    min_octet = 0
    octets = 4
    bits_per_octet = 8

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
            self.ip = copy.deepcopy(ip_list)
        else:
            raise ValueError("IP input must be either (string) ip_string (EX: 10.0.0.0) or " +
                "(list) ip_list (EX. [10,0,0,0])")
        self.validate()
        return

    def validate(self):
        """Validates IP."""
        if len(self.ip) != 4:
            raise ValueError(f"{self}: octet count must be 4. EX: 255.255.255.255")
        if self.ip[0] == 0:
            raise ValueError(f"{self}: first octet cannot be 0 as it is reserved.")
        for octet in self.ip:
            if octet < IP.min_octet or octet > IP.max_octet:
                raise ValueError(f"{self}: octets must be integers <= 255 and >= 0. EX: 255.125.221.0")
        return

    def __str__(self):
        """String representation."""
        return ".".join([str(ip) for ip in self.ip])

    def __sub__(self, other):
        """Subtraction override that represents the # of hosts between IPs."""
        return abs(self._to_numerical() - other._to_numerical()) + 1

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

    def _to_numerical(self):
        """# of hosts between IP and 0.0.0.0"""
        total = 0
        for i in range(len(self.ip)):
            total += self.ip[i]*((IP.max_octet+1)**(abs(i-(IP.octets-1))))
        return total

    def _from_numerical(self, num):
        """
        From # of hosts between IP and 0.0.0.0 to an IP address.
        """
        ip = []
        left = num
        for i in range(len(self.ip)):
            octet_val = (IP.max_octet+1)**(abs(i-(IP.octets-1)))
            ip.append(left // octet_val)
            left -= (ip[-1] * octet_val)
        return ip

    def add_hosts(self, hosts):
        """Increase the IP address by # hosts."""
        self.ip = IP.if_add_hosts(self, hosts).ip
        return self

    @classmethod
    def if_add_hosts(cls, ip, hosts):
        """Preview of what happens if you add # hosts."""
        current = ip._to_numerical()
        return cls(ip_list=ip._from_numerical(current + hosts))

    def remove_hosts(self, hosts):
        """Decrease the IP address by # hosts."""
        self.ip = IP.if_remove_hosts(self, hosts).ip
        return self

    @classmethod
    def if_remove_hosts(cls, ip, hosts):
        """Preview of what happens if you remove # hosts."""
        current = ip._to_numerical()
        return cls(ip_list=ip._from_numerical(current - hosts))