#!/usr/bin/env python3

import socket
import struct
import utilities as util
import json
import os
from threading import Thread

def sendFile(fname, conn, mypath):
    fpath = mypath + fname
    f = open(fpath, 'rb')
    l = f.read(1024)
    while (l):
        conn.send(l)
        l = f.read(1024)
    f.close()


def sendIndex(flag, args, conn, mypath):
    table = util.listFiles(flag, args, mypath)
    tosend = json.dumps(table)
    conn.send(tosend.encode())


def sendHash(flag, args, conn, mypath):
    table = util.listHash(flag, args, mypath)
    tosend = json.dumps(table)
    conn.send(tosend.encode())


def recvCommand(conn, mypath):
    data = conn.recv(struct.calcsize('II'))
    cmd, argSize = struct.unpack('II', data)
    # print(cmd, argSize)
    if cmd == 1:   # index
        arg = conn.recv(argSize).decode().split(' ')
        flag = arg[0]
        args = arg[1:]
        # print(cmd, flag, args)
        sendIndex(flag, args, conn, mypath)
    elif cmd == 2: # hash
        arg = conn.recv(argSize).decode().split(' ')
        flag = arg[0]
        args = arg[1:]
        # print(cmd, flag, args)
        sendHash(flag, args, conn, mypath)
    elif cmd == 3: # download
        arg = conn.recv(argSize)
        # print(cmd, arg.decode())
        sendFile(arg.decode(), conn, mypath)

class Server(Thread):
    def __init__(self, mypath = './files_server/', port = 60000):
        # , mypath = './files_server', port = 60000
        Thread.__init__(self)
        self.mypath = mypath
        host = os.environ.get('host') or ""
        self.s = socket.socket()
        self.s.bind((host, port))
        self.s.listen(5)

    def run(self):
        while True:
            conn, addr = self.s.accept()
            # print('Got connection from', addr)
            recvCommand(conn, self.mypath)
            # print('Done sending')
            conn.close()
