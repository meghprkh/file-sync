#!/usr/bin/env python3

import sys
import struct
import socket
import json
import utilities as util
import os

mypath = os.environ.get('dir') or './files_client/'
host = os.environ.get('host') or ""
port = int(os.environ.get('port') or 60000)


############## Client functions ##############

def downloadFile(fname, sock):
    fpath = mypath + fname
    servermd5 = struct.unpack('256s', sock.recv(256))[0].decode()
    with open(fpath, 'wb') as f:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            # write data to a file
            f.write(data)
    clientmd5 = util.getmd5(fpath)
    print('server checksum', servermd5)
    print('client checksum', clientmd5)
    print('successful transfer?', servermd5.startswith(clientmd5))

def downloadIndex(sock):
    stru = ''
    while True:
        data = sock.recv(1024)
        if not data:
            break
        stru += data.decode()
    util.prettyprint(json.loads(stru))


############## Communication ##############

def sendCommand(cmd, arg):
    sock = socket.socket()
    sock.connect((host, port))
    if cmd == 1:   # index
        sock.send(struct.pack('II', 1, sys.getsizeof(arg)))
        sock.send(arg.encode())
        downloadIndex(sock)
        pass
    elif cmd == 2: # hash
        sock.send(struct.pack('II', 2, sys.getsizeof(arg)))
        sock.send(arg.encode())
        downloadIndex(sock)
        pass
    elif cmd == 3: # download
        sock.send(struct.pack('II', 3, sys.getsizeof(arg)))
        sock.send(arg.encode())
        downloadFile(arg, sock)
    sock.close()




############## Main ##############

if __name__ == '__main__':
    while True:
        cmd = input('>> ')
        cmd = cmd.split(' ', 1)
        if cmd[0] == 'index':
            sendCommand(1, cmd[1])
            pass
        elif cmd[0] == 'hash':
            sendCommand(2, cmd[1])
            pass
        elif cmd[0] == 'download':
            sendCommand(3, cmd[1])
