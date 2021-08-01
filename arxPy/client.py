#!/usr/bin/env python3
import platform, subprocess, requests, json, os

'''
Client side python framework for arxPy API.
'''

class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class client:

    def __init__(self, host, port=80):
        self.host = host
        self.port = port
        self.url = f'{self.host}:{self.port}'
        self.home = os.path.expanduser('~')

    def timeFrameData(self, pair, startDate, stopDate):
        pkg = Object()
        pkg.pair = pair
        pkg.mode = 'timeframe'
        pkg.start = startDate
        pkg.stop = stopDate
        response = requests.post(self.url, json=pkg.toJSON()) #, cert=(f'{self.certDir}/key.pem', f'{self.certDir}/cert.pem') )
        response.encoding = response.apparent_encoding
        print(response.text)

if __name__ == '__main__':
    c = client('http://localhost', 8080)
    c.timeFrameData('AAVEUSD', '07-31-21 20:25', '07-31-21 23:20')