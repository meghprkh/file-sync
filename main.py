#!/usr/bin/env python3

import sys
from os import listdir
import os.path as op
import mimetypes

mypath = '.'
shared_files = []
shared_files = [f for f in listdir(mypath) if op.isfile(op.join(mypath, f))]

def getType(fpath):
    return mimetypes.guess_type(fpath)[0]

def listFiles(flag, args):
    print('name\tsize\ttimestamp\ttype')
    for f in shared_files:
        fpath = op.join(mypath, f)
        print(f + '\t' + str(op.getsize(fpath)) + '\t' + str(op.getmtime(fpath)) + '\t' + getType(fpath))


if __name__ == '__main__':
    if sys.argv[1] == 'index':
        listFiles(sys.argv[2], sys.argv[3:])
