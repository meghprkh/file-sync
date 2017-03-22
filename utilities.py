#!/usr/bin/env python3

from os import listdir
import os.path as op
import mimetypes
import re
import hashlib

def prettyprint(data, shouldPrint = True):
    if data == -1 and shouldPrint:
        print('ERROR: File does not exist')
        return
    stru = ''
    col_width = max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        stru += "".join(word.ljust(col_width) for word in row) + '\n'
    if shouldPrint:
        print(stru)
    return stru

def getFiles(mypath):
    shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]
    for f in listdir(mypath):
        if op.isdir(op.join(mypath, f)):
            rec_files = getFiles(op.join(mypath, f))
            shared_files += [op.join(f, fr) for fr in rec_files]
    return shared_files

def listFiles(flag, args, mypath):
    def getType(fpath):
        if op.isdir(fpath):
            return 'directory'
        return mimetypes.guess_type(fpath)[0] or 'text/plain'

    ############## List Files ##############
    shared_files = listdir(mypath)
    table = [['Name', 'Type', 'Timestamp', 'Type']]
    for f in shared_files:
        fpath = op.join(mypath, f)
        time = getmtime(fpath)
        if flag == 'shortlist':
            if time < int(args[0]) or time > int(args[1]):
                continue
        elif flag == 'regex':
            if not re.fullmatch('.*' + args[0], f):
                continue
        table.append([f, str(op.getsize(fpath)), str(time), getType(fpath)])

    return table



def getmd5(fpath):
    with open(fpath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

def getmtime(fpath):
    return int(op.getmtime(fpath))

def getUpdateDetails(fpath):
    return (getmd5(fpath), getmtime(fpath))


def listHash(flag, args, mypath):
    shared_files = getFiles(mypath)
    table = [['Name', 'Checksum', 'Timestamp']]
    if flag == 'verify':
        shared_files = [args[0]]
        if not op.exists(args[0]):
            return -1
    for f in shared_files:
        fpath = op.join(mypath, f)
        time = getmtime(fpath)
        table.append([f, str(getmd5(fpath)), str(time)])

    return table
