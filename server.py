#!/usr/bin/env python3

import socket
import struct

port = 60000
s = socket.socket()
host = ""

s.bind((host, port))
s.listen(5)

def recvCommand():
    data = conn.recv(struct.calcsize('II'))
    cmd, argSize = struct.unpack('II', data)
    # print(cmd, argSize)
    if cmd == 1:   # index
        pass
    elif cmd == 2: # hash
        pass
    elif cmd == 3: # download
        arg = conn.recv(argSize)
        print(cmd, arg.decode())

while True:
    conn, addr = s.accept()
    print('Got connection from', addr)
    recvCommand()

    print('Done sending')
    conn.send('Thank you for connecting'.encode())
    conn.close()
