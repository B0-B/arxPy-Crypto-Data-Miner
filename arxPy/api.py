#!/usr/bin/env python3

'''
    Simple rest API based on barebone-ssl-wrapped network socket which listens to HTTP packages.
'''

import os
import json
import http.server, ssl, cgi
from threading import Thread
from traceback import print_exc
try:
    from tools import arxive, log
except:
    from arxPy.tools import arxive, log

class Object:

    def toJSON(self):

        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

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
            
        # read the request message and convert it to json
        jsonPkg = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        dic = json.loads(jsonPkg) # double loads turns to dict
        log(f"received package (type {type(dic)}):\n\t{jsonPkg}")


        # check which mode was picked
        responsePkg = Object()
        responsePkg.pair = dic['pair']
        try:
            if dic['mode'] == 'timeframe':
                try:
                    rows = self.arx.queryPeriod(dic['pair'], dic['start'], dic['stop'])
                    responsePkg.data = rows
                except Exception as e:
                    print(e)
                    responsePkg.error = 'No data for given time period'
        except Exception as e:
            print_exc()
            responsePkg.error = e
        finally:
            self.end_headers()
            self.wfile.write(responsePkg.toJSON().encode('utf-8'))     

class server:

    def __init__(self, port, handler):

        # invoke server
        self.httpd = http.server.HTTPServer(('localhost', port), handler)

        # Pointer -> thread
        self.thread = None

    def invoke(self):
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()