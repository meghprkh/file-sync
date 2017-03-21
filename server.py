#!/usr/bin/env python3

import socket
import struct
import utilities as util
import json


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


def sendIndex(flag, args, conn):
    table = util.listFiles(flag, args, mypath)
    tosend = json.dumps(table)
    conn.send(tosend.encode())


def sendHash(flag, args, conn):
    table = util.listHash(flag, args, mypath)
    tosend = json.dumps(table)
    conn.send(tosend.encode())


def recvCommand():
    data = conn.recv(struct.calcsize('II'))
    cmd, argSize = struct.unpack('II', data)
    # print(cmd, argSize)
    if cmd == 1:   # index
        arg = conn.recv(argSize).decode().split(' ')
        flag = arg[0]
        args = arg[1:]
        print(cmd, flag, args)
        sendIndex(flag, args, conn)
        pass
    elif cmd == 2: # hash
        arg = conn.recv(argSize).decode().split(' ')
        flag = arg[0]
        args = arg[1:]
        print(cmd, flag, args)
        sendHash(flag, args, conn)
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
