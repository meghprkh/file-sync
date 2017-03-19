#!/usr/bin/env python3

import socket
import struct
from os import listdir
import os.path as op
import mimetypes
import re
import hashlib

mypath = './files_server/'

port = 60000
s = socket.socket()
host = ""

s.bind((host, port))
s.listen(5)

def prettyprint(data):
    stru = ''
    col_width = max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        stru += "".join(word.ljust(col_width) for word in row) + '\n'
    return stru

def sendFile(fname, conn):
    fpath = mypath + fname
    f = open(fpath, 'rb')
    l = f.read(1024)
    while (l):
        conn.send(l)
        l = f.read(1024)
    f.close()


def sendIndex(flag, args, conn):
    def getType(fpath):
        return mimetypes.guess_type(fpath)[0] or 'text/plain'

    ############## List Files ##############
    shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]
    table = [['Name', 'Type', 'Timestamp', 'Type']]
    for f in shared_files:
        fpath = op.join(mypath, f)
        time = op.getmtime(fpath)
        if flag == 'shortlist':
            if time < float(args[0]) or time > float(args[1]):
                continue
        elif flag == 'regex':
            if not re.fullmatch('.*' + args[0], f):
                continue
        table.append([f, str(op.getsize(fpath)), str(time), getType(fpath)])

    tosend = prettyprint(table)
    conn.send(tosend.encode())


def sendHash(flag, args, conn):
    def getmd5(fpath):
        with open(fpath, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    def getUpdateDetails(fpath):
        return (getmd5(fpath), op.getmtime(fpath))

    shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]
    table = [['Name', 'Checksum', 'Timestamp']]
    if flag == 'verify':
        shared_files = [args[0]]
    for f in shared_files:
        fpath = op.join(mypath, f)
        time = op.getmtime(fpath)
        table.append([f, str(getmd5(fpath)), str(time)])

    tosend = prettyprint(table)
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
