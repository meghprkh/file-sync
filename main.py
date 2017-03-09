#!/usr/bin/env python3

import sys
from os import listdir
import os.path as op
import mimetypes
import re

mypath = '.'
shared_files = []
shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]

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

if __name__ == '__main__':
    if sys.argv[1] == 'index':
        listFiles(sys.argv[2], sys.argv[3:])
