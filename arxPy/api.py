#!/usr/bin/env python3

'''
    Simple rest API based on barebone-ssl-wrapped network socket which listens to HTTP packages.
'''

import os
import json
import http.server, ssl, cgi
from threading import Thread

class handler(http.server.SimpleHTTPRequestHandler):

    '''
    Main for handling json packages
    '''

    # def do_GET(self):
    #     self.send_response(200)
        
    #     #self.end_headers()

    #     # receive package
    #     self.

    #     # package json
    #     Json = json.load({})

    #     self.wfile.write(html.encode())

    def do_POST(self):

        # send an ok first
        self.send_response(200)

        # send header
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        #length = int(self.headers.getheader('content-length'))
        self.data_string = self.rfile.read(int(self.headers['Content-Length'])).decode('utf8')
        print(self.data_string)
        #message = json.loads(self.rfile.read(self.data_string))
        

        #print(message)


class server:

    def __init__(self, port, handler):

        # check for ssl certificate
        # self.home = os.path.expanduser('~')
        # self.certDir = self.home + '/certificate'
        # self.certPath = self.certDir + '/arxpy_cert.pem'
        # if not os.path.isdir(self.certDir):
        #     os.system(f'mkdir {self.certDir}')
        #     print('Create ssl certificate ...')
        #     os.system(f'''openssl req -newkey rsa:2048 -new -nodes -x509 -keyout {self.certPath} -out {self.certPath}''')
        
        # invoke server
        self.httpd = http.server.HTTPServer(('localhost', port), handler)
        # self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
        #                             server_side=True,
        #                             certfile=self.certPath,
        #                             ssl_version=ssl.PROTOCOL_TLS)

        # Pointer -> thread
        self.thread = None

    def invoke(self):
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.run()

if __name__ == '__main__':
    a = server(8080, handler)
    a.httpd.serve_forever()