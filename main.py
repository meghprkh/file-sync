#!/usr/bin/env python3

import sys
import struct
import socket


mypath = './files_client/'


############## Client functions ##############

def downloadFile(fname, sock):
    fpath = mypath + fname
    with open(fpath, 'wb') as f:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            # write data to a file
            f.write(data)

def downloadIndex(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(data.decode())


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
    port = 60000
    host = ""

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
