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


# class pipe(threading.Thread):

#     def __init__(self, function, wait, *args):
#         self.wait = wait
#         threading.Thread.__init__(self)
#         self.func = function
#         self.args = args
#         self.stoprequest = threading.Event()

#     def run(self):
#         while not self.stoprequest.isSet():
#             try: # important during init, otherwise crash
#                 self.func(*self.args)
                
#                 # listen frequently during waiting
#                 for i in range(10*self.wait):
#                     if self.stoprequest.isSet():
#                         break
#                     sleep(.1)
#             except:
#                 pass

#     def stop(self, timeout = None):
#         self.stoprequest.set()
#         super(pipe, self).join(timeout)

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
        #self.data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        jsonPkg = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        self.data = json.loads(jsonPkg) # double loads turns to dict
        dic = self.data
        # print('datastring', self.data_string)
        # pkg = json.dumps(self.data_string)
        # #JSON = json.loads(''.join(pkg.split('\\'))[2:-2])
        # dic = json.loads(pkg)
        log(f"received package (type {type(dic)}):\n\t{jsonPkg}")


        # check which mode was picked
        responsePkg = Object()
        try:
            #raise ValueError('TEst')
            if dic['mode'] == 'timeframe':
                rows = self.arx.queryPeriod(dic['pair'], dic['start'], dic['stop'])
                print('rows', rows)
                responsePkg.data = rows
        except Exception as e:
            print_exc()
            responsePkg.error = e
        finally:
            #responseDump = json.dumps(responsePkg)
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

if __name__ == '__main__':
    a = server(8080, handler)
    a.httpd.serve_forever()