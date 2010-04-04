#!/usr/bin/python

import asyncore, socket
import json

from defines import *

# updates from in_client, and then we write to out_client
remotes = {}
remotes_updated = False

class OutServer(asyncore.dispatcher):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('0.0.0.0', OUT_SERVER_PORT))
        self.listen(1)
        self.buffer = ''
        self._connected = []

    def update_all(self, buffer):
        buffer = buffer + '\n'
        for x in self._connected:
            x.update_buffer(buffer)
            x.handle_write()
        self.buffer = buffer

    def handle_accept(self):
        channel, addr = self.accept()
        self._connected.append(OutServerHandler(channel, self))

    def _on_closed(self, c):
        del self._connected[self._connected.index(c)]

class OutServerHandler(asyncore.dispatcher):

    def __init__(self, s, parent):
        asyncore.dispatcher.__init__(self, s)
        self._parent = parent
        self._buffer = parent.buffer

    def handle_connect(self):
        print "connected - %r" % self._buffer

    def update_buffer(self, b):
        self._buffer = b

    def writable(self):
        return len(self._buffer)

    def handle_write(self):
        print "writing %r" % self._buffer
        try:
            sent = self.send(self._buffer)
        except:
            self.handle_close()
            return
        self._buffer = self._buffer[sent:]

    def handle_close(self):
        self._parent.on_closed(self)

class InServer(asyncore.dispatcher):

    def __init__(self, out):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('0.0.0.0', IN_SERVER_PORT))
        self.listen(1)
        self._out = out

    def handle_accept(self):
        channel, addr = self.accept()
        InServerHandler(channel, self._out)

class InServerHandler(asyncore.dispatcher):

    def __init__(self, parent, out):
        asyncore.dispatcher.__init__(self, parent)
        self._out = out
        self._data = []

    def handle_read(self):
        #import pdb; pdb.set_trace()
        new_data = self.recv(8192)
        if len(new_data.strip()) == 0: return
        self._data.append(new_data)
        try:
            host, ip = (''.join(self._data)).strip().split(',')
        except:
            return
        remotes[host] = ip
        self._out.update_all(buffer=json.dumps(remotes))

if __name__ == '__main__':
    out_server = OutServer()
    in_server = InServer(out_server)
    asyncore.loop()

