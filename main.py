#!/usr/bin/env python3

import sys
from os import listdir
import os.path as op
import mimetypes
import re
import hashlib
import struct
import socket


mypath = '.'
shared_files = []
shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]


############## List Files ##############

def prettyprint(data):
    col_width = max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        print("".join(word.ljust(col_width) for word in row))

def getType(fpath):
    return mimetypes.guess_type(fpath)[0] or 'text/plain'

def listFiles(flag, args):
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
    prettyprint(table)



############## Hash Files ##############

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



############## Communication ##############

def sendCommand(cmd, arg):
    sock = socket.socket()
    sock.connect((host, port))
    if cmd == 1:   # index
        pass
    elif cmd == 2: # hash
        pass
    elif cmd == 3: # download
        sock.send(struct.pack('II', 3, sys.getsizeof(arg)))
        sock.send(arg.encode())
    sock.close()




############## Main ##############

if __name__ == '__main__':
    port = 60000
    host = ""

    while True:
        cmd = input('>> ')
        cmd = cmd.split(' ')
        if cmd[0] == 'index':
            pass
        elif cmd[0] == 'hash':
            pass
        elif cmd[0] == 'download':
            sendCommand(3, cmd[-1])
