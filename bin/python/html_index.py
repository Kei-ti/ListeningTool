#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Keiti, Kou Tanaka'
__version__ = '1.0'
__license__ = __author__

import os
import sys
import numpy as np
import argparse

from html_template import HTML
from configure import load_jsonfile

def walk_files_with(extension, directory='.'):
    """Generate paths of all files that has specific extension in a directory. 

    Arguments:
    extension -- [str] File extension without dot to find out
    directory -- [str] Path to target directory

    Return:
    filepath -- [str] Path to file found
    """
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith('.' + extension):
                yield os.path.join(root, filename)


def header():
    html = ['<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset=“utf-8″>',
            '<title>Start page</title>',
            '<script type="text/javascript" src="/bin/javascript/browser.js"></script>',
            '</head>',
            '<body>',
            '<noscript><p class="attention">Based on your setting, javaScript is disable. Please check it.</p></noscript>']

    return html

def footer():
    html = ['</body>',
            '<script type="text/javascript">',
            '<!--',
            '    document.getElementById("hidden_browser_type").value=get_browser();',
            '//-->',
            '</script>',
            '</html>']

    return html

def main(confdir, outf):
    html = HTML(0, header=False)
    html.html += header()

    html.html += ['<form action="/bin/python/html.py" method="post">']
    for i, jsonfile in enumerate(walk_files_with("json", directory=confdir)):
        html.html += ['  <input type="radio" name="jsonfile" value="{}" required/>{}<br>'.format(jsonfile, os.path.basename(os.path.splitext(jsonfile)[0]))]

    html.html += ['  <input type="hidden" name="index" value="0"/>',
                  '  <input type="hidden" name="browser" value="x" id="hidden_browser_type"/>',
                  '  <input type="submit" name="button" value="next"/>',
                  '</form>']

    html.html += footer()

    html.draw(outf=outf, footer=False)    

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='create/check index html file')
    parser.add_argument('-d', '--directory',
                        type=str,
                        action='store',
                        default='configure',
                        help='directory of configure')
    parser.add_argument('-o', '--output',
                        type=str,
                        action='store',
                        default='index.html',
                        help='filename of output')
    args = parser.parse_args()

    main(args.directory, args.output)

