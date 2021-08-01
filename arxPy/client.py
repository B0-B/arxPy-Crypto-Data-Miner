#!/usr/bin/env python3
import platform, subprocess, requests, json, os

'''
Client side python framework for arxPy API.
'''

class client:

    def __init__(self, host, port=80):
        self.host = host
        self.port = port
        self.url = f'{self.host}:{self.port}'
        self.home = os.path.expanduser('~')
        # self.certDir = self.home + '/certs'
        # self.certPath = self.certDir + '/arxpy_cert.pem'
        # if not os.path.isdir(self.certDir):
        #     os.system(f'mkdir {self.certDir}')
        #     os.system(f'''openssl req -newkey rsa:2048 -new -nodes -x509 -keyout {self.certDir}/key.pem -out {self.certDir}/cert.pem''')

    def timeFrameData(self, pair, startDate, endDate):
        pkg = json.dumps({
            "pair": pair,
            "mode": 'timeframe',
            "start": startDate,
            "end": endDate
        })
        response = requests.post(self.url, json=pkg) #, cert=(f'{self.certDir}/key.pem', f'{self.certDir}/cert.pem') )
        response.encoding = response.apparent_encoding
        print(response.text)

if __name__ == '__main__':
    c = client('http://localhost', 8080)
    c.timeFrameData('XBTEUR', '', '')