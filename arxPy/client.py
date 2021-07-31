#!/usr/bin/env python3
import platform, subprocess, requests

'''
Client side python framework for arxPy API.
'''

class client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f'{self.host}:{self.port}'

    def timeFrameData(self, pair, startDate, endDate):
        pkg = json.load({
            "mode": 'timeframe',
            "start": startDate,
            "end": endDate
        })
        response = requests.post(self.url, json=pkg) 
        print(response.json())

if __name__ == '__main__':
    c = client('https://localhost', 4433)
    c.timeFrameData()