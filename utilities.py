#!/usr/bin/env python3

from os import listdir
import os.path as op
import mimetypes
import re
import hashlib

def prettyprint(data):
    stru = ''
    col_width = max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        stru += "".join(word.ljust(col_width) for word in row) + '\n'
    return stru


def listFiles(flag, args, mypath):
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

def getUpdateDetails(fpath):
    return (getmd5(fpath), op.getmtime(fpath))


def listHash(flag, args, mypath):
    shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]
    table = [['Name', 'Checksum', 'Timestamp']]
    if flag == 'verify':
        shared_files = [args[0]]
    for f in shared_files:
        fpath = op.join(mypath, f)
        time = op.getmtime(fpath)
        table.append([f, str(getmd5(fpath)), str(time)])

    return table
