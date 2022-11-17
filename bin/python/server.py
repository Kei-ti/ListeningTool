#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Keiti, Kou Tanaka'
__version__ = '1.0'
__license__ = __author__

import os
import sys
import argparse
#import numpy as np

import socket
import http.server
import socketserver
#import threading

#import email.utils
#import html
#import http.client
#import io
#import mimetypes
#import os
#import posixpath
#import select
#import shutil
#import socket # For gethostbyaddr()
#import socketserver
#import sys
#import time
import urllib.parse
#import copy

from http import HTTPStatus

import re


class HTTPServer(socketserver.TCPServer):
    #address_family = socket.AF_UNIX
    request_queue_size = 10
    allow_reuse_address = 1    # Seems to make sense in testing environment

    def server_bind(self):
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        #print(self.socket)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

class ForkedHTTPServer(socketserver.ForkingMixIn, HTTPServer):
    pass

class MYHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve a GET request."""
        self.range_from, self.range_to = self.get_range_header()
        if self.range_from is None:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        f = self.send_range_head()
        if f:
            self.copy_file_range(f, self.wfile)
            f.close()

    def do_HEAD(self): 
        """Serve a HEAD request.""" 
        self.range_from, self.range_to = self.get_range_header()
        if self.range_from is None:
            return http.server.SimpleHTTPRequestHandler.do_HEAD(self)
        f = self.send_range_head()
        if f:
            f.close()

    def copy_file_range(self, in_file, out_file):
        """ Copy only the range in self.range_from/to. """
        in_file.seek(self.range_from)
        # Add 1 because the range is inclusive
        left_to_copy = 1 + self.range_to - self.range_from
        buf_length = 64*1024
        bytes_copied = 0
        while bytes_copied < left_to_copy:
            read_buf = in_file.read(min(buf_length, left_to_copy - bytes_copied))
            #read_buf = in_file.read(min(buf_length, left_to_copy))
            if len(read_buf) == 0:
                break
            out_file.write(read_buf)
            bytes_copied += len(read_buf)
        return bytes_copied

    def send_range_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """

        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                if True: # Don't show the list of files in directory
                    self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                    return None
                else:
                    return self.list_directory(path)
        #if not exists(path) and path.endswith('/data'):
        #    # Fixme: Handle grits-like query with /data appended to path
        #    # stupid grits
        #    if exists(path[:-5]):
        #        path = path[:-5]
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        #try:
        #    self.send_response(HTTPStatus.OK)
        #    fs = os.fstat(f.fileno())
        #    self.send_header("Content-type", ctype)
        #    self.send_header("Content-Length", str(fs[6]))
        #    self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        #    self.end_headers()
        #    sys.stderr.write("Content-type: {}\n".format(ctype))
        #    sys.stderr.write("Content-Length: {}\n".format(fs[6]))
        #    return f
        try:
            if self.range_from is None:
                self.send_response(HTTPStatus.OK)
            else:
                self.send_response(HTTPStatus.PARTIAL_CONTENT)

            self.send_header("Content-type", ctype)
            sys.stderr.write("Content-type: {}\n".format(ctype))
            fs = os.fstat(f.fileno())
            if self.range_from is not None:
                if self.range_to is None or self.range_to >= fs[6]:
                    self.range_to = fs[6]-1
                self.send_header("Content-Range",
                                 "bytes %d-%d/%d" % (self.range_from,
                                                     self.range_to,
                                                     fs[6]))
                # Add 1 because ranges are inclusive
                self.send_header("Content-Length", (1 + self.range_to - self.range_from))
                #sys.stderr.write("Content-Length: {}\n".format(1 + self.range_to - self.range_from))
                #sys.stderr.write("Content-Range: bytes {}-{}/{}\n".format(self.range_from,self.range_to,fs[6]))
            else:
                self.send_header("Content-Range", "bytes */%d" % (fs[6]))
                self.send_header("Content-Length", str(fs[6]))
                #sys.stderr.write("Content-Length: {}\n".format(fs[6]))
                #sys.stderr.write("Content-Range: bytes */{}\n".format(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def get_range_header(self):
        """ Returns request Range start and end if specified.
        If Range header is not specified returns (None, None)
        """
        range_header = self.headers["Range"]
        if range_header is None:
            return (None, None)
        if not range_header.startswith("bytes="):
            #print("Not implemented: parsing header Range: {}".format(range_header))
            return (None, None)
        regex = re.compile(r"^bytes=(\d+)\-(\d+)?")
        rangething = regex.search(range_header)
        if rangething:
            from_val = int(rangething.group(1))
            if rangething.group(2) is not None:
                return (from_val, int(rangething.group(2)))
            else:
                return (from_val, None)
        else:
            print('CANNOT PARSE RANGE HEADER:'.format(range_header))
            return (None, None)

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                if True: # Don't show the list of files in directory
                    self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                    return None
                else:
                    return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            self.send_response(HTTPStatus.OK)
            fs = os.fstat(f.fileno())
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            #sys.stderr.write("Content-type: {}\n".format(ctype))
            #sys.stderr.write("Content-Length: {}\n".format(fs[6]))
            return f
        except:
            f.close()
            raise

class MYCGIHandler(MYHandler, http.server.CGIHTTPRequestHandler):
    def send_head(self):
        """Version of send_head that support CGI scripts"""
        if self.is_cgi():
            return self.run_cgi()
        else:
            return MYHandler.send_head(self)

    def is_cgi(self):
        collapsed_path = http.server._url_collapse_path(self.path)
        for path in self.cgi_directories:
            if path in collapsed_path:
                dir_sep_index = collapsed_path.rfind(path) + len(path)
                head, tail = collapsed_path[:dir_sep_index], collapsed_path[dir_sep_index + 1:]
                self.cgi_info = head, tail
                return True
        return False

def run(HandlerClass=MYHandler,
         ServerClass=ThreadedHTTPServer, protocol="HTTP/1.0", port=8000):
    """Test the HTTP request handler class.
    This runs an HTTP server on port 8000 (or the port argument).
    """
    server_address = (socket.gethostbyname(socket.gethostname()), port)
    #server_address = ("", port)

    HandlerClass.protocol_version = protocol
    with ServerClass(server_address, HandlerClass) as httpd:
        sa = httpd.socket.getsockname()
        serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
        print(serve_message.format(host=sa[0], port=sa[1]))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='server')
    parser.add_argument('--nocgi',
                        action='store_true',
                        help='Run as NOT cgi Server')
    parser.add_argument('--thread',
                        action='store_true',
                        help='Run Threading HTTP Server')
    #parser.add_argument('--process',
    #                    action='store_true',
    #                    help='Run Processing HTTP Server')
    parser.add_argument('--port',
                        type=int,
                        action='store',
                        default=8000,
                        help='port number [default: 8000]')
    args = parser.parse_args()
    #args = parser.parse_args("--cgi --process --port 8007".split(" "))
    #args = parser.parse_args("--port 8012".split(" "))

    if args.nocgi:
        print("NOT CGIServer")
        handler_class = MYHandler
    else:
        print("CGIServer")
        handler_class = MYCGIHandler
        handler_class.cgi_directories = ['/bin/python']

    if args.thread:
        print("ThreadedHTTPServer")
        server_class = ThreadedHTTPServer
    #elif args.process:
    else:
        print("ForkedHTTPServer")
        server_class = ForkedHTTPServer
    #else:
    #    server_class = HTTPServer

    run(ServerClass=server_class, HandlerClass=handler_class, port=args.port)

"""

def main(ip, port):
   
    Handler = http.server.CGIHTTPRequestHandler

    with socketserver.ThreadingTCPServer(("{}".format(ip), port), Handler) as httpd:
        httpd.server_name = "evaluation"
        httpd.serve_forever()

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='server')
    parser.add_argument('-p', '--port',
                        type=int,
                        action='store',
                        default=8000,
                        help='port number (default: 8000)')
    args = parser.parse_args()

    print("plaese open: http://{}:{}".format(get_ip()[1],args.port))
    main(get_ip()[1], args.port)

"""

     
