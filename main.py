#!/usr/bin/env python3

import struct
import socket
import json
import utilities as util
import os
import os.path as op
from threading import Thread, Timer
from server import Server


class Client(Thread):
    def __init__(self, mypath = './files_client/', port = 60000, ownServerPort = 60001):
        Thread.__init__(self)
        self.host = ""
        self.port = port
        self.ownServerPort = ownServerPort
        self.mypath = mypath
        self.autosync = True
        self.syncThread = Timer(2, self.sync)
        self.syncThread.start()

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
                self.sendCommand(4, '')
                self.syncThread.cancel()
                break
            elif cmd[0] == "autosync":
                self.autosync = not self.autosync


    def sendCommand(self, cmd, arg, noprint = False):
        sock = socket.socket()
        if cmd == 4:
            port = self.ownServerPort
        else:
            port = self.port
        sock.connect((self.host, port))
        s = bytes(arg, 'utf-8')
        data = struct.pack("II%ds" % (len(s),), cmd, len(s), s)
        sock.send(data)
        retval = ''
        if cmd == 1:   # index
            print('# Server shared files')
            retval = self.downloadIndex(sock, noprint)
            print('# Client shared files')
            arg = arg.split(' ')
            flag = arg[0]
            args = arg[1:]
            util.prettyprint(util.listFiles(flag, args, self.mypath))
        elif cmd == 2: # hash
            if not noprint:
                print('# Server shared files')
            retval = self.downloadIndex(sock, noprint)
            if not noprint:
                print('# Client shared files')
                arg = arg.split(' ')
                flag = arg[0]
                args = arg[1:]
                util.prettyprint(util.listHash(flag, args, self.mypath))
        elif cmd == 3: # download
            arg = arg.split(' ')
            isUDP = arg[0] == 'UDP'
            fname = arg[1]
            size = 0
            if isUDP:
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect((self.host, self.port))
                sock.send(fname.encode())
                size = sock.recv(4)
                size, = struct.unpack('I', size)
            retval = self.downloadFile(isUDP, fname, sock, size)
        sock.close()
        return retval

    def downloadFile(self, isUDP, fname, sock, size = 0):
        print('Downloading ' + fname)
        fpath = op.join(self.mypath, fname)
        diru = fpath.rsplit("/", 1)
        if len(diru) == 2:
            diru = diru[0]
            if not op.exists(diru):
                os.makedirs(diru)
        perm = sock.recv(4)
        perm, = struct.unpack('I', perm)
        with open(fpath, 'wb') as f:
            recvtillnow = 0
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                # write data to a file
                f.write(data)
                recvtillnow += 1024
                if recvtillnow > size and isUDP:
                    break
        clientmd5 = util.getmd5(fpath)
        updatedetails = self.sendCommand(2, 'verify ' + fname, True)[1]
        servermd5 = updatedetails[1]
        os.utime(fpath, (op.getatime(fpath), int(updatedetails[2])))
        os.chmod(fpath, perm)
        print('server checksum', servermd5)
        print('client checksum', clientmd5)
        print('successful transfer?', servermd5.startswith(clientmd5))
        print('Size', op.getsize(fpath), '\tTimestamp', util.getmtime(fpath))

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
        self.syncThread = Timer(2, self.sync)
        self.syncThread.start()
        if not self.autosync:
            return
        didPrint = False
        sfiles = self.sendCommand(2, 'checkall', True)[1:]
        ofiles = util.getFiles(self.mypath)
        for r in sfiles:
            # print(r)
            fname = r[0]
            shouldDownload = False
            if fname in ofiles:
                hs = util.getUpdateDetails(self.mypath + fname)
                if hs[0] != r[1]:
                    if hs[1] < r[2]:
                        shouldDownload = True
            else:
                shouldDownload = True

            if shouldDownload:
                if not didPrint:
                    print('Autosyncing')
                    didPrint = True
                self.sendCommand(3, 'TCP ' + fname)

        if didPrint:
            print('\n>> ', end='')


############## Main ##############

if __name__ == '__main__':
    port = int(os.environ.get('port') or 60000)
    port2 = port + 1 if port % 2 == 0 else port - 1
    port2 = int(os.environ.get('port2') or port2)
    diru = './dir1/' if port % 2 == 0 else './dir2/'
    diru = os.environ.get('dir') or diru

    server = Server(diru, port)
    client = Client(diru, port2, port)

    server.start()
    client.start()

    server.join()
    client.join()
