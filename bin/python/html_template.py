#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Keiti, Kou Tanaka'
__version__ = '1.0'
__license__ = __author__

import os
import sys
import codecs
import numpy as np

##############################################
###              HTML TEMPLATE             ###
##############################################
class HTML():
    def __init__(self, browser, title="Blank", header=True):
        """
            browser:
                0: Internet Exprolar
                1: Safari
                2: Chrome
                Others: [undefined]
        """
        assert browser in [0, 1, 2]
        self.browser = browser
        self.title = title

        # initialize flagment
        self.flag_style = False
        self.flag_header = False
        self.flag_footer = False
        self.flag_draw = False

        # initialize html file
        self.html = []
        if header:
            print('Content-type: text/html; charset=UTF-8\n')
            self._header()
    
    def draw(self, outf="", footer=True):
        assert self.flag_draw == False
        self.flag_draw = True

        if footer:
            self._footer()

        if outf != "":
            if os.path.dirname(outf) not in ["", "."]:
                os.makedirs(os.path.dirname(outf), exist_ok=True)
            out=codecs.open(outf, "w", "utf-8")
        else:
            out=sys.stdout

        for html in self.html:
            print(html, file=out)

        if outf != "":
            out.close()

    def _header(self):
        assert self.flag_header == False
        self.flag_header = True

        self.html += \
            ['<!DOCTYPE html>',
             '<html>'
             '<head>'
             '<meta charset=“utf-8″>',
             '<title>{}</title>'.format(self.title),
             '<STYLE type="text/css"><!--']
        self._style()
        self.html += \
            ['--></STYLE>',
             '</head>',
             '<body>']

    def _style(self):
        assert self.flag_style == False
        self.flag_style = True

        self.html += \
            ['  div.soundfile {',
             '    margin: 1em 0px;',
             '    padding: 0.5em 1em;',
             '    border: 1px solid gray;',
             '  }']
        self.html += \
            ['  div.imagefile {',
             '    margin: 1em 0px;',
             '    padding: 0.5em 1em;',
             '    border: 1px solid gray;',
             '  }']

    def _footer(self):
        assert self.flag_footer == False
        self.flag_footer = True

        self.html += \
            ['</body>',
             '</html>']

    def _path(self, inf, system=False):
        def _path_root(inf):
            if list(inf)[0] != "/": return "/{}".format(inf)
            return inf

        def _path_dot(inf):
            if list(inf)[0] == "/": return ".{}".format(inf)
            return "./{}".format(inf)

        if system: return _path_dot("{}".format(inf))
        else: return _path_root("{}".format(inf))

    def plain(self, *args):
        """
            args = list[str(text1), ...]
        """
        if len(args) == 0: return

        for text in args:
            self.html += \
                ['<p>{}</p>'.format(text)]


    def imgviewer(self, key, val):
        imgf = self._path(val)
        assert os.path.isfile(self._path(imgf, system=True))

        self.html += \
            ['<div class="imgfile">',
             '  <p>Image: {}</p>'.format(key)]
        self.html += \
            ['  <img src="{}">'.format(imgf)]
        self.html += ['</div>']

    def audioplayer(self, key, val):
        wavf = self._path(val)
        assert os.path.isfile(self._path(wavf, system=True))

        self.html += \
            ['<div class="soundfile">',
             '  <p>Sound: {}</p>'.format(key)]
        if self.browser in [0]:
            # browser is a Internet Exprolar
            activex = "http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=6,4,7,1112"
            self.html += \
                ['  <object type="application/x-oleobject"',
                 '    classid="CLSID:22D6f312-B0F6-11D0-94AB-0080C74C7E95"',
                 '    standby="Loading Windows Media Player components..."',
                 '    width="320 " height="44"',
                 '    codebase="{}">'.format(activex),
                 '    <param name="AutoStart" value="false" />',
                 '    <param name="AutoRewind" value="true" />',
                 '    <param name="AutoSize" value="false" />',
                 '    <param name="AllowChangeDisplaySize" value="false" />',
                 '    <param name="AllowScan" value="false" />',
                 '    <param name="ClickToPlay" value="true" />',
                 '    <param name="FileName" value="{}" />'.format(wavf),
                 '    <param name="ShowControls" value="true" />',
                 '    <param name="ShowAudioControls" value="true" />',
                 '    <param name="ShowCaptioning" value="false" />',
                 '    <param name="ShowDisplay" value="false" />',
                 '    <param name="ShowGotoBar" value="false" />',
                 '    <param name="ShowPositionControls" value="false" />',
                 '    <param name="ShowStatusBar" value="false" />',
                 '    <param name="ShowTracker" value="true" />',
                 '    <param name="Enabled" value="true" />',
                 '    <param name="EnableTracker" value="true" />',
                 '    <param name="EnableFullScreenControls" value="false" />',
                 '    <param name="EnableContextMenu" value="false" />'
                 '  </object>']
        elif self.browser in [1, 2]:
            # browser is a Safari or Chrome
            self.html += \
                ['  <audio preload="auto" controlslist="nodownload" controls>',
                 '    <source src="{}" type="audio/wav"></source>'.format(wavf),
                 '    <p>Cannot play on your browser...</p>',
                 '  </audio>']

        self.html += ['</div>']

    def form(self, action, hiddens={}, radios={}, radio_checks={}):
        """
            To send some information to next page:
                hiddens = dict{key1:str(val1), ...}

            To prepare radio botton:
                radios = dict{key1:list[str(val1), ...], ...}

            To check radio botton as default:
                radio_checks = dict{key1:str(val1), ...}
        """

        self.html += ['<form action="{}" method="post">'.format(action)]

        # for hiddens
        for (key, val) in list(hiddens.items()):
            self.html += \
                ['  <input type="hidden" name="{}" value="{}"/>'.format(key,val)]

        # for radios
        for (key, vals) in list(radios.items()):
            assert isinstance(vals, list)
            if key in radio_checks.keys(): valch = radio_checks[key]
            else: valch = None
            self.html += ['  {}: '.format(key)]
            for val in vals:
                if valch == val: check = "checked"
                else: check = ""
                self.html += \
                    ['  <input type="radio" name="{}" value="{}" required {}/>{}'.format(key,val,check,val)]
            self.html += ['  <br>']

        self.html += \
            ['  <input type="button" name="button" value="back" onClick="history.back()">',
             '  <input type="submit" name="button" value="next"/>',
             '</form>']

    def show_results_as_table(self, npzfile, gt_len=0, gt_keys=[]):
        """
            npzfile: str(path)
            gt_len : int(length)
            gt_keys: list[str(key1), ...]

            Note that npz: {key1:np.array, ...}
            The length of each np.array is gt_len.
        """
        assert os.path.isfile(npzfile)

        dat = dict(np.load(npzfile))

        # check
        for key in gt_keys:
            assert key in dat.keys()
            assert len(dat[key]) == gt_len

        self.html += \
            ['<table border=1>',
             '  <thead bgcolor="#cc99ff" style="color:#000000">',
             '    <tr>',
             '      <th>Index</th>']

        for key in gt_keys:
            self.html += \
                ['      <th>{}</th>'.format(key)]

        self.html += \
            ['    </tr>',
             '  </thead>',
             '  <tbody>']

        for idx in range(gt_len):
            self.html += \
                ['    <tr>'
                 '      <th bgcolor="#cccccc">{}</th>'.format(idx+1)]

            for key in gt_keys:
                self.html += \
                    ['      <th>{}</th>'.format(dat[key][idx])]

            self.html += \
                ['    </tr>']

        self.html += \
            ['  </tbody>',
             '</table>']

