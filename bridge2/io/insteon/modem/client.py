from __future__ import absolute_import, division, print_function, unicode_literals
import collections
import gevent
import gevent.event
import gevent.select
from bridge2.io.insteon.modem.core import *
from bridge2.io.insteon.modem.messages import *

#
# High-level modem interface
#

class _AsyncModemInterface(ModemInterface):
    def __init__(self, port):
        super(AsyncModemInterface, self).__init__(port)
        self._dev.timeout = 0
        self._dev.writeTimeout = 0
    
    def _doread(self, n):
        # Use select to yield until the device is ready, then write
        data = ""
        nread = 0
        while nread < n:
            gevent.select.select([self._dev], [], [])
            data2 = self._dev.read(n)
            nread += len(data2)
            data += data2
        return data

    def _dowrite(self, data):
        # Use select to yield until the device is ready, then write
        n = len(data)
        nwritten = 0
        while nwritten < n:
            gevent.select.select([], [self._dev], [])
            nwritten += self._dev.write(data[nwritten:])
        return n

class InsteonClient(object):
    def __init__(self, port):
        assert isinstance(port, unicode)
        self._port = port
        self._pendingmsgs = {}
    
    def _handlemsgresp(self, pdu):
        # Signal a waiting sendmsg call
        msgdata = pdu.payload[:-1]
        arq = self._pendingmsgs.get(msgdata)
        ar = arq.popleft()
        if len(arq) == 0:
            del self._pendingmsgs[msgdata]
        ar.set(pdu.successful)

    @property
    def port(self):
        return self._port

    def _run(self):
        try:
            while True:
                pdu = self._iface.recv()
                handler = self._handlers.get(type(pdu))
                if handler != None:
                    handler(pdu)
        finally:
            self._active = False

    def sendmsg(self, dest, msg):
        """Transmit an InsteonMessage via the modem, waiting for
           acknowledgement or failure. This function yields to other
           greenthreads."""
        # Validate arguments
        assert isinstance(dest, bytes) and len(dest) == 3
        assert isinstance(msg, InsteonMessage)
        assert (msg.mclass & 0b011) == 0 # DIRECT_CMD or BROADCAST_CMD
        
        # Produce a PDU for the message
        pdu = SendInsteonMsgModemPDU(dest, msg)
        
        # Create an event in order to wait for a modem ACK/NAK
        arq = self._pendingmsgs.get(pdu.payload)
        if arq == None:
            arq = collections.deque()
            self._pendingmsgs[pdu.payload] = arq
        ar = gevent.event.AsyncResult()
        ars.append(ar)
        
        # Transmit the PDU and wait for an ACK/NAK from the modem
        self._iface.send(pdu)
        successful = ar.get()
        if not successful:
            raise IOError(b"Message transmission failed")

    def start(self):
        """Start the receive loop on a dedicated greenthread."""
        assert not self._active
        self._iface = _AsyncModemInterface(port)
        try:
            self._active = True
            self._greenlet = gevent.spawn(self._run)
        except:
            self._active = False
            raise
        
    def stop():
        """Terminate the receive loop."""
        assert self._active
        self._greenlet.kill(block=True)

    _handlers = {
        SendInsteonMsgModemPDU.Response: _handlemsgresp
    }
