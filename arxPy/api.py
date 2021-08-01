#!/usr/bin/env python3

'''
    Simple rest API based on barebone-ssl-wrapped network socket which listens to HTTP packages.
'''

import os
import json
import http.server, ssl, cgi
from threading import Thread
try:
    from tools import arxive
except:
    from arxPy.tools import arxive

class handler(http.server.SimpleHTTPRequestHandler):

    '''
    Main for handling json packages
    '''

    arx = arxive(os.path.dirname(os.path.abspath(__file__))+'/../data/ohlc.db')

    def do_POST(self):

        # send an ok first
        self.send_response(200)

        # send header
        self.send_header('Content-type', 'application/json')
        
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        self.data_string = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        pkg = json.dumps(self.data_string)
        JSON = json.loads(''.join(pkg.split('\\'))[2:-2])
        print("received package:", pkg)


        # check which mode was picked
        if pkg['mode'] == 'timeframe':
            pass

        self.end_headers()

class server:

    def __init__(self, port, handler):

        # invoke server
        self.httpd = http.server.HTTPServer(('localhost', port), handler)

        # Pointer -> thread
        self.thread = None

    def invoke(self):
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.run()

if __name__ == '__main__':
    a = server(8080, handler)
    a.httpd.serve_forever()