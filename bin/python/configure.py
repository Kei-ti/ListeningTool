#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Keiti, Kou Tanaka'
__version__ = '1.0'
__license__ = __author__

import os
#import sys
import json
import argparse
import numpy as np


def load_listfile(listfile):
    assert os.path.isfile(listfile)
    
    dat = np.genfromtxt(listfile, dtype=str)

    if len(dat.shape) == 1:
        return dat.reshape(-1,1)
    elif len(dat.shape) == 2:
        return dat
    else:
        assert False

def check_contents(listfile, datas, criterions):
    assert os.path.isfile(listfile)
    assert isinstance(datas, list)
    assert isinstance(criterions, dict)
    for key in criterions.keys():
        assert isinstance(criterions[key], list)

    dat = load_listfile(listfile)
    
    assert dat.shape[-1] == len(datas)
    for filename in dat.flatten():
        assert os.path.isfile(filename)

def load_jsonfile(jsonfile):
    if not True:
        listfile = "configure/list/test.list"
        resultfile = "result/case1.npz"
        datas = ["X", "A", "B"]
        criterions = {"Similarity":["A", "B", "Fair"], "Quality":["A", "B", "Fair"]}
    else:
        assert os.path.isfile(jsonfile)
        with open(jsonfile, 'r') as f:
            dicts = json.load(f)

        assert "list" in dicts.keys()
        assert "result" in dicts.keys()
        assert "datas" in dicts.keys()
        assert "criterions" in dicts.keys()
        listfile = dicts["list"]
        resultfile = dicts["result"]
        datas = dicts["datas"]
        criterions = dicts["criterions"]

    check_contents(listfile, datas, criterions)

    return listfile, resultfile, datas, criterions

def save_jsonfile(outf, listfile, resultfile, datas, criterions):
    if os.path.dirname(outf) not in ["", "."]:
        os.makedirs(os.path.dirname(outf), exist_ok=True)
    if resultfile is None:
        resultfile = "result/{}.npz".format(os.path.splitext(os.path.basename(outf))[0])

    check_contents(listfile, datas, criterions)

    dicts = {"list":listfile, "result":resultfile, "datas":datas, "criterions":criterions}

    if os.path.isfile(outf):
        os.remove(outf)

    with open(outf,'w') as f:
        json.dump(dicts, f, indent=4)

    assert os.path.isfile(outf)


def print_out(listfile, resultfile, datas, criterions):
    print("--- Configure ----")
    print("   listfile is...")
    print("      {}\n".format(listfile))
    print("   resultfile is...")
    print("      {}\n".format(resultfile))
    print("   data keys are...")
    print("      {}\n".format(datas))
    print("   criterions are...")
    for i, key in enumerate(criterions.keys()):
        print("      {}: {}".format(key, criterions[key]))
    print("------------------")

def compose(listfile, datas, criterions):
    res = {}
    res["listfile"] = listfile
    res["datas"] = datas


def parse_datas(arg):
    return arg.split(',')

def parse_criterions(args):
    """
        args: list[str(key1:val1,...,valN), ..., str(keyN:val1,...,valN)]
        
        Ex) ["Similarity:A,B,Fair", "Quality:1,2,3,4,5"]

    """
    res = {}
    for arg in args:
        assert arg.count(":") == 1
        key, vals = arg.split(':')[0], arg.split(':')[1]
        res[key] = vals.split(',')

    return res

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='create/check configure file')
    parser.add_argument('-c', '--criterions',
                        type=str,
                        nargs='+',
                        action='store',
                        help='Criterions of evaluations')
    parser.add_argument('-l', '--list',
                        type=str,
                        action='store',
                        help='filename of a list')
    parser.add_argument('-d', '--datas',
                        type=str,
                        action='store',
                        help='data Keys')
    parser.add_argument('-t', '--types',
                        type=str,
                        action='store',
                        help='data types')
    parser.add_argument('-j', '--json',
                        type=str,
                        action='store',
                        required=True,
                        help='filename of json')
    parser.add_argument('-o', '--output',
                        type=str,
                        action='store',
                        default=None,
                        help='filename of evaluation result')
    parser.add_argument('--inv',
                        action='store_true',
                        default=False,
                        help='Load configure file')
    args = parser.parse_args()
    #args = parser.parse_args("-l configure/list/test.list -d X,A,B -t -c Similarity:A,B,Fair Quality:A,B,Fair -j configure/test.json -o result/test.npz".split(" "))
    #args = parser.parse_args("--inv -o configure/test.json".split(" "))

    if args.inv:
        load_jsonfile(args.json)
    else:
        listfile = args.list
        resultfile = args.output
        datas = parse_datas(args.datas)
        criterions = parse_criterions(args.criterions)

        if not True:
            # check
            print_out(listfile, resultfile, datas, criterions)

        # save
        save_jsonfile(args.json, listfile, resultfile, datas, criterions)



