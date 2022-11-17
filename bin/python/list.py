#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import numpy as np
import random
import fnmatch

class util:
    class io:
        class path:
            def mkdirname(path):
                if os.path.dirname(path) not in ["", "."]:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
        
            def remove(path, directory=False):
                if os.path.isfile(path): os.remove(path)
                elif os.path.isdir(path) and directory: os.rmdir(path)

        class gnu:
            def find(directory, name="*"):
                for root, dirnames, filenames in os.walk(directory):
                    for filename in filenames:
                        if fnmatch.fnmatch(filename, name):
                            yield os.path.join(root, filename)


def XAB(dirs, outf, exts):
    assert len(dirs) == 3
    dirs = {"X":dirs[0], "A":dirs[1], "B":dirs[2]}

    # main
    lists = {}
    for key in dirs.keys():
        lists[key] = []
    for key in dirs.keys():
        for ext in exts:
            for filename in sorted(util.io.gnu.find(dirs[key], name="*.{}".format(ext))):
                lists[key].append(filename)
    res = []
    for key in dirs.keys():
        res += [random.sample(sorted(lists[key]), len(lists[key]))]
    res = np.array(res)
    for i in range(len(res[0])):
        if 0.5 > np.random.rand():
            res[1][i], res[2][i] = res[2][i], res[1][i]

    # output
    util.io.path.mkdirname(outf)
    util.io.path.remove(outf)
    np.savetxt(outf, res.transpose(), fmt="%s")

def AB(dirs, outf, exts):
    assert len(dirs) == 2
    dirs = {"A":dirs[0], "B":dirs[1]}

    # main
    lists = {}
    for key in dirs.keys():
        lists[key] = []
    for key in dirs.keys():
        for ext in exts:
            for filename in sorted(util.io.gnu.find(dirs[key], name="*.{}".format(ext))):
                lists[key].append(filename)
    res = []
    for key in dirs.keys():
        res += [random.sample(sorted(lists[key]), len(lists[key]))]
    res = np.array(res)
    for i in range(len(res[0])):
        if 0.5 > np.random.rand():
            res[0][i], res[1][i] = res[1][i], res[0][i]

    # output
    util.io.path.mkdirname(outf)
    util.io.path.remove(outf)
    np.savetxt(outf, res.transpose(), fmt="%s")

def MOS(dirs, outf, exts):
    assert len(exts) == 1
    # main
    lists = []
    for key in dirs:
        for ext in exts:
            for filename in sorted(util.io.gnu.find(key, name="*.{}".format(ext))):
                lists.append(filename)
    res = random.sample(sorted(lists), len(lists))
    res = np.array(res)
    # output
    util.io.path.mkdirname(outf)
    util.io.path.remove(outf)
    np.savetxt(outf, res.transpose(), fmt="%s")

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='create_list')
    parser.add_argument('-d', '--dirs',
                        nargs='+',
                        type=str,
                        action='store',
                        required=True,
                        help='the directories')
    parser.add_argument('-o', '--out',
                        type=str,
                        action='store',
                        required=True,
                        help='the output file')
    parser.add_argument('--XAB',
                        action='store_true',
                        default=False,
                        help='XAB test')
    parser.add_argument('--AB',
                        action='store_true',
                        default=False,
                        help='AB test')
    parser.add_argument('--MOS',
                        action='store_true',
                        default=False,
                        help='MOS test')
    parser.add_argument('--DMOS',
                        action='store_true',
                        default=False,
                        help='DMOS test')
    parser.add_argument('-e','--exts',
                        nargs='+',
                        type=str,
                        action='store',
                        help='extension')
    args = parser.parse_args()
    
    if args.XAB:
        XAB(args.dirs, args.out, args.exts)
    elif args.AB:
        AB(args.dirs, args.out, args.exts)
    elif args.MOS:
        MOS(args.dirs, args.out, args.exts)
    else:
        print("Undefined.")
        assert False


