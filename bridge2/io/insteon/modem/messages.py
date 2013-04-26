"""
Create an Insteon command by calling the appriate object
with the correct information.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import binascii

class InsteonMessage(object):
    """Represents a standard-length Insteon message, and serves as a base
       class for all other types of Insteon message objects."""
    DIRECT_CMD = 0b000
    DIRECT_ACK = 0b001
    LINK_CLEANUP_CMD = 0b010
    LINK_CLEANUP_ACK = 0b011
    BROADCAST_CMD = 0b100
    DIRECT_NAK = 0b101
    LINK_BROADCAST_CMD = 0b110
    LINK_CLEANUP_NAK = 0b111
    
    _mcnames = {
        DIRECT_CMD: "D",
        DIRECT_ACK: "D ACK",
        LINK_CLEANUP_CMD: "C",
        LINK_CLEANUP_ACK: "C ACK",
        BROADCAST_CMD: "B",
        DIRECT_NAK: "D NAK",
        LINK_BROADCAST_CMD: "A",
        LINK_CLEANUP_NAK: "C NAK"
    }
    
    def __init__(self, mclass, c1, c2, ttl=None, max_ttl=None):
        # Validate arguments
        assert mclass >= 0 and mclass <= 0b111
        if ttl == None:
            ttl = 3 if (mclass & 0b101) == 0b100 else 1
        if max_ttl == None:
            max_ttl = 3 if (mclass & 0b101) == 0b100 else 1
        assert ttl >= 0 and ttl <= 3
        assert max_ttl >= 0 and max_ttl <= 3
        assert c1 >= 0 and c1 <= 0xFF
        assert c2 >= 0 and c2 <= 0xFF
        
        # Store values
        self._mclass = mclass
        self._ttl = ttl
        self._max_ttl = max_ttl
        self._c1 = c1
        self._c2 = c2

    @property
    def c1(self):
        """Return the first command byte for this InsteonMessage."""
        return self._c1
    
    @property
    def c2(self):
        """Return the second command byte for this InsteonMessage."""
        return self._c2

    @classmethod
    def decode(cls, buf):
        """Decode a bytestring into an InsteonMessage."""
        assert isinstance(buf, bytes)
        rv = cls.__new__(cls)
        rv._decode(buf)
        return rv

    def _decode(self, buf):
        assert len(buf) == 3
        flags = ord(buf[0])
        self._mclass = flags >> 5
        ext = (flags & 0b10000) != 0
        if ext != self.extended:
            raise ValueError("An unexpected message type was encountered")
        self._ttl = (flags >> 2) & 0b11
        self._max_ttl = flags & 0b11
        self._c1 = ord(buf[1])
        self._c2 = ord(buf[2])
        
    def encode(self):
        """Encode this InsteonMessage as a bytestring."""
        flags = 0
        flags |= self._mclass << 5
        flags |= (0b10000 if self.extended else 0)
        flags |= self._ttl << 2
        flags |= self._max_ttl
        return chr(flags) + chr(self._c1) + chr(self._c2)

    @property
    def extended(self):
        """Return whether or not this InsteonMessage is an extended message."""
        return False
    
    @property
    def max_ttl(self):
        """Return the maximum number of forwards permitted for this
           InsteonMessage."""
        return self._max_ttl
    
    @property
    def mclass(self):
        """Return the message class of this InsteonMessage."""
        return self._mclass

    @property
    def ttl(self):
        """Return the remaining number of forwards permitted for this
           InsteonMessage."""
        return self._ttl

    def __str__(self):
        return self.__unicode__().encode()

    def __unicode__(self):
        fmt = "{0} message {1:#02x}:{2:02x}, {3}/{4} hops"
        mcn = "E" if self.extended else "S"
        mcn += InsteonMessage._mcnames[self._mclass]
        return fmt.format(mcn, self._c1, self._c2, self._ttl, self._max_ttl)

class ExtInsteonMessage(InsteonMessage):
    """Represents an extended-length Insteon message."""
    def __init__(self, mclass, c1, c2, extdata, ttl=None, max_ttl=None):
        assert isinstance(extdata, bytes)
        assert len(extdata) == 14
        super(ExtInsteonMessage, self).__init__(mclass, c1, c2, ttl, max_ttl)
        self._extdata = extdata
    
    def _decode(self, buf):
        assert len(buf) == 17
        super(ExtInsteonMessage, self)._decode(buf[0:3])
        self._extdata = buf[3:17]
    
    def encode(self):
        """Encode this ExtInsteonMessage as a bytestring."""
        basebuf = super(ExtInsteonMessage, self).encode()
        return basebuf + self._extdata
    
    @property
    def extdata(self):
        """Return the extended data from this ExtInsteonMessage."""
        return self._extdata
    
    @property
    def extended(self):
        return True

    def __unicode__(self):
        basestr = super(ExtInsteonMessage, self).__unicode__()
        return basestr + ", payload = " + binascii.hexlify(self._extdata)
