#!/usr/bin/env python3

import struct
import socket
import json
import utilities as util
import os
import os.path as op
from threading import Thread
from server import Server
import time


class Client(Thread):
    def __init__(self, mypath = './files_client/', port = 60000):
        Thread.__init__(self)
        self.host = ""
        self.port = port
        self.mypath = mypath
        self.lastSync = time.time()

    def run(self):
        while True:
            cmd = input('>> ')
            cmd = cmd.split(' ', 1)
            if cmd[0] == 'index':
                self.sendCommand(1, cmd[1])
                pass
            elif cmd[0] == 'hash':
                self.sendCommand(2, cmd[1])
                pass
            elif cmd[0] == 'download':
                self.sendCommand(3, cmd[1])
            elif cmd[0] == "exit":
                break

            curTime = time.time()
            if curTime - self.lastSync > 2:
                self.lastSync = curTime
                self.sync()

    def sendCommand(self, cmd, arg, noprint = False):
        sock = socket.socket()
        sock.connect((self.host, self.port))
        s = bytes(arg, 'utf-8')
        data = struct.pack("II%ds" % (len(s),), cmd, len(s), s)
        sock.send(data)
        if cmd == 1:   # index
            print('# Server shared files')
            retval = self.downloadIndex(sock, noprint)
            print('# Client shared files')
            arg = arg.split(' ')
            flag = arg[0]
            args = arg[1:]
            util.prettyprint(util.listFiles(flag, args, self.mypath))
        elif cmd == 2: # hash
            print('# Server shared files')
            retval = self.downloadIndex(sock, noprint)
            print('# Client shared files')
            arg = arg.split(' ')
            flag = arg[0]
            args = arg[1:]
            util.prettyprint(util.listHash(flag, args, self.mypath))
        elif cmd == 3: # download
            retval = self.downloadFile(arg, sock)
        sock.close()
        return retval

    def downloadFile(self, fname, sock):
        print('Downloading ' + fname)
        fpath = self.mypath + fname
        with open(fpath, 'wb') as f:
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                # write data to a file
                f.write(data)
        clientmd5 = util.getmd5(fpath)
        updatedetails = self.sendCommand(2, 'verify ' + fname, True)[1]
        servermd5 = updatedetails[1]
        os.utime(fpath, (op.getatime(fpath), int(updatedetails[2])))
        print('server checksum', servermd5)
        print('client checksum', clientmd5)
        print('successful transfer?', servermd5.startswith(clientmd5))

    def downloadIndex(self, sock, noprint = False):
        stru = ''
        while True:
            data = sock.recv(1024)
            if not data:
                break
            stru += data.decode()
        if noprint:
            return json.loads(stru)
        util.prettyprint(json.loads(stru))

    def sync(self):
        print('Autosyncing')
        sfiles = self.sendCommand(2, 'checkall', True)[1:]
        ofiles = [f for f in os.listdir(self.mypath) if op.isfile(op.join(self.mypath, f))]
        for r in sfiles:
            # print(r)
            fname = r[0]
            if fname in ofiles:
                hs = util.getUpdateDetails(self.mypath + fname)
                if hs[0] != r[1]:
                    if hs[1] < r[2]:
                        self.sendCommand(3, fname)
            else:
                self.sendCommand(3, fname)


############## Main ##############

if __name__ == '__main__':
    port = int(os.environ.get('port') or 60000)
    port2 = port + 1 if port % 2 == 0 else port - 1
    port2 = int(os.environ.get('port2') or port2)
    diru = './dir1/' if port % 2 == 0 else './dir2/'
    diru = os.environ.get('dir') or diru

    server = Server(diru, port)
    client = Client(diru, port2)

    server.start()
    client.start()

    server.join()
    client.join()
