#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Keiti, Kou Tanaka'
__version__ = '1.0'
__license__ = __author__

import os
import sys
import cgi
import cgitb
import numpy as np
from shutil import copyfile

from html_template import HTML
from configure import load_jsonfile, load_listfile

######################################
#  --- HOW TO WRITE the Console ---  #
#                                    #
# Instead of print(""), please use   #
#   sys.stderr.write("\n")           #
#   sys.stdout.write("\n")           #
######################################

def script():
    return os.path.basename(__file__)

def check():
    assert os.environ['REQUEST_METHOD'] in ["POST"]
    return cgi.FieldStorage()

def sample(form):
    """ form is a object of dict """
    html = HTML(0, title="test")
    #print(form)
    html.plain("This is a sample.")
    html.draw()

######################################
#def get_result_path(listfile, prefix=""):
#    return "./result/{}{}.npz".format(prefix,os.path.basename(listfile))

def check_files(listfile, dim=1):
    lists = load_listfile(listfile)
    assert dim == lists.shape[1]
    for filename in lists.flatten():
        assert os.path.isfile(filename)

def save_result(form, outf, listfile, idx, keys=[], prefix=""):
    assert len(keys) != 0
    for key in keys:
        assert key in form.keys()

    if idx not in [0, 1]:
        assert os.path.isfile(outf)

    if os.path.dirname(outf) not in ["", "."]:
        os.makedirs(os.path.dirname(outf), exist_ok=True)

    dat = {}
    if os.path.isfile(outf):
        dat = dict(np.load(outf))
        for key in keys:
            assert key in dat.keys()
    else:
        for key in keys:
            dat[key] = np.zeros(0, dtype=str)

    for key in keys:
        if len(dat[key]) > idx:
            dat_key = list(dat[key])
            dat_key[idx] = "{}".format(form[key].value)
            dat[key] = np.array(dat_key)
        else:
            dat[key] = np.array(list(dat[key])+["{}".format(form[key].value)])
        #sys.stderr.write("{}: {}\n".format(key, form[key].value))

    np.savez(outf, **dat)

def get_radio_checks(outf, listfile, idx, keys=[], prefix=""):
    assert len(keys) != 0

    if os.path.isfile(outf):
        dat = dict(np.load(outf))
        res = {}
        for key in keys:
            assert key in dat.keys()
            if len(dat[key]) <= idx: return {}
            res[key] = dat[key][idx]
        #sys.stderr.write("{}\n".format(res))
        return res
    else:
        return {}

def get_viewers(filenames, idx, keys):
    res = {}
    for i, key in enumerate(keys):
        res[key] = filenames[idx, i]
    return res


######################################
def main(form):
    # check
    assert "jsonfile" in form.keys()
    assert "index" in form.keys()
    assert "browser" in form.keys()
    assert form["browser"].value in map(str, range(-1,6))
    browser = int(form["browser"].value)
    index = int(form.getfirst("index"))
    jsonfile = form["jsonfile"].value
    assert index >= 0

    # required
    listfile, outf, datas, criterions = load_jsonfile(jsonfile)
    """
        Example:

        listfile = "configure/list/test.list"
        listfile = "result/test.npz"
        datas = ["X", "A", "B"]
        criterions = {"Similarity":["A", "B", "Fair"], "Quality":["A", "B", "Fair"]}
    """

    # main
    next_script = "/bin/python/{}".format(script())
    filenames = load_listfile(listfile)
    if index == 0: check_files(listfile, dim=len(datas))
    else: save_result(form, outf, listfile, index-1, keys=criterions.keys(), prefix="")
    if index < len(filenames):
        html = HTML(browser, title="Evaluation")
        html.plain("Index {} / {}".format(index+1,len(filenames)))

        viewers = get_viewers(filenames, index, datas)
        for key, val in list(viewers.items()):
            #print(os.path.splitext(val)[1].lower())
            if os.path.splitext(val)[1].lower() in [".jpg", ".jpeg", ".png", ".gif", ".bpm"]:
                html.imgviewer(key, val)
            elif os.path.splitext(val)[1].lower() in [".wav", ".mp3"]:
                html.audioplayer(key, val)
            else:
                print("Error: Undefined extention of {}".format(val))
                print(key, val, os.path.splitext(val)[1].lower())

        radio_checks = get_radio_checks(outf, listfile, index, keys=criterions.keys(), prefix="")
        html.form(
            next_script,
            hiddens={"browser":browser, "jsonfile":jsonfile, "index":index+1}, # always required
            radios=criterions,
            radio_checks=radio_checks)

        html.draw()
    else:
        outfno = 1
        while True:
            outffinal = "{}.version.{}".format(outf, outfno)
            if os.path.isfile(outffinal):
                outfno += 1
                continue
            copyfile(outf, outffinal)
            break
        html = HTML(browser, title="Thx")
        html.plain("Thank you! :)")
        html.plain("Please close a window.")
        html.plain("If any blank on a scoreboard, please let me know.")
        html.show_results_as_table(
            outf,
            gt_len=len(filenames),
            gt_keys=criterions.keys())
        html.draw()


if __name__ == '__main__':
    cgitb.enable()
    form = check()

    if not True:
        sample(form)
    else:
        main(form)


