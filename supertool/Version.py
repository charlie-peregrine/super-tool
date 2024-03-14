"""basic version class for making comparing and printing the supertool version easier"""
# Version.py, Charlie Jordan, 3/8/2024
# basic version class for making comparing and printing the supertool version easier

import re

class Version():
    """
    basic version class for comparing and printing the supertool version easier
    """
    
    def __init__(self, maj_: int | str, min_: int | None = None,
            pat_: int | None = None):
        if isinstance(maj_, str):
            m = re.match(r'^v(\d+)\.(\d+)\.(\d+)$', maj_)
            if m:
                self.major = int(m.group(1))
                self.minor = int(m.group(2))
                self.patch = int(m.group(3))
            else:
                raise ValueError(f"Invalid Version String: {maj_}")
        elif isinstance(maj_, int) and isinstance(min_, int) and isinstance(pat_, int):
            self.major = maj_
            self.minor = min_
            self.patch = pat_
        else:
            raise ValueError(f"Invalid Version Arguments: {maj_}, {min_}, {pat_}")
    
    def __str__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"
    
    def _tuple(self):
        return (self.major, self.minor, self.patch)
    
    def __lt__(self, other):
        for left, right in zip(self._tuple(), other._tuple()):
            if left < right:
                return True
            if left > right:
                return False
        return False
    
    def __eq__(self, other):
        return self._tuple() == other._tuple()
    
    def __le__(self, other):
        return self < other or self == other
