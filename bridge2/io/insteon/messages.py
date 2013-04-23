"""
Create an Insteon command by calling the appriate object
with the correct information.
"""

import binascii

class InsteonMessage(object):
    """Base class for all insteon commands."""
    
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
    
    def __init__(self, mclass, ttl, max_ttl, c1, c2):
        # Validate arguments
        assert mclass >= 0 and mclass <= 0b111
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
        return self._c1
    
    @property
    def c2(self):
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
        """Encode the message as a bytestring."""
        flags = 0
        flags |= self._mclass << 5
        flags |= (0b10000 if self.extended else 0)
        flags |= self._ttl << 2
        flags |= self._max_ttl
        return chr(flags) + chr(self._c1) + chr(self._c2)

    @property
    def extended(self):
        return False
    
    @property
    def max_ttl(self):
        return self._max_ttl
    
    @property
    def mclass(self):
        return self._mclass

    @property
    def ttl(self):
        return self._ttl

    def __str__(self):
        return self.__unicode__().encode()

    def __unicode__(self):
        fmt = "{0} message {1:#02x}:{2:02x}, {3}/{4} hops"
        mcn = "E" if self.extended else "S"
        mcn += InsteonMessage._mcnames[self._mclass]
        return fmt.format(mcn, self._c1, self._c2, self._ttl, self._max_ttl)

class ExtInsteonMessage(InsteonMessage):   
    def __init__(self, mclass, ttl, max_ttl, c1, c2, extdata):
        assert isinstance(extdata, bytes)
        assert len(extdata) == 14
        super(ExtInsteonMessage, self).__init__(mclass, ttl, max_ttl, c1, c2)
        self._extdata = extdata
    
    def _decode(self, buf):
        assert len(buf) == 17
        super(ExtInsteonMessage, self)._decode2(buf[0:3])
        self._extdata = buf[3:17]
    
    def encode(self):
        basebuf = super(ExtInsteonMessage, self)
        return basebuf + self._extdata
    
    @property
    def extdata(self):
        return self._extdata
    
    @property
    def extended(self):
        return True

    def __unicode__(self):
        basestr = super(ExtInsteonMessage, self).__unicode__()
        return basestr + ", payload = " + binascii.hexlify(self._extdata)
