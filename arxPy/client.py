#!/usr/bin/env python3
import requests, urllib.request, json, os

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
        return json.loads(response.text)

    def allData(self, pair):
        pkg = Object()
        pkg.pair = pair
        pkg.mode = 'all'
        response = requests.post(self.url, json=pkg.toJSON()) #, cert=(f'{self.certDir}/key.pem', f'{self.certDir}/cert.pem') )
        response.encoding = response.apparent_encoding
        return json.loads(response.text)
    
    def coins (self, base="usd"):
        '''
        Returns all coin symbols available on kraken.
        '''

        # -- request --
        request = urllib.request.Request("https://api.kraken.com/0/public/AssetPairs")

        # -- validate --
        ticket = urllib.request.urlopen(request)
        raw_data = ticket.read()
        encoding = ticket.info().get_content_charset('utf8')
        result = json.loads(raw_data.decode(encoding))['result'].keys()
        out, base = [], base.upper()
        for pair in result:
            if base in pair:
                validName=True
                for elem in out:
                    if elem in pair:
                        validName=False
                        break
                if validName:
                    out.append(pair.replace(base, ''))
        return out

if __name__ == '__main__':
    c = client('http://localhost', 8080)
    c.timeFrameData('AAVEUSD', '07-31-21 20:25', '07-31-21 23:35')
    c.coins()