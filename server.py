#!/usr/bin/env python3

import socket
import struct

mypath = './files_server/'

port = 60000
s = socket.socket()
host = ""

s.bind((host, port))
s.listen(5)

def sendFile(fname, conn):
    fpath = mypath + fname
    f = open(fpath, 'rb')
    l = f.read(1024)
    while (l):
        conn.send(l)
        l = f.read(1024)
    f.close()

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
        sendFile(arg.decode(), conn)

while True:
    conn, addr = s.accept()
    print('Got connection from', addr)
    recvCommand()
    print('Done sending')
    conn.close()
