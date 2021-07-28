# modules
import json
import urllib
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
from datetime import datetime, timedelta


class kraken:

    URL = 'https://api.kraken.com/0/public/OHLC'

    def coins (self, base="usd"):
        '''
        Returns all coin symbols available on kraken.
        '''

        # -- request --
        request = Request("https://api.kraken.com/0/public/AssetPairs")

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

    def OHLC (self, pair, intervalInMinutes, epochInMinutes):
            
        '''
        provide epoch parameter as unix timestamp
        exp.:   OHLC("XRPEUR", 5, 1440) for ripple timeseries data on 5 min interval
                of the last 24 hours. This yields 1440/5=288 data points <=> returned list length.
        '''

        # -- validate input --
        if type(pair) is not str or len(pair) == 0:
            raise TypeError(f'pair must be of type str e.g. "XRPEUR" not type {type(intervalInMinutes)}')
        if type(intervalInMinutes) is not int:
            raise TypeError(f'intervalInMinutes must be of type int not {type(intervalInMinutes)}')
        elif type(epochInMinutes) is not int:
            raise TypeError(f'epochInMinutes must be of type int not {type(epochInMinutes)}')
            
        # -- build data package and encode --
        # convert epoch into unix timestamp
        now = datetime.now()
        past = now - timedelta(minutes=epochInMinutes)
        data = {
            'pair' : pair,
            'interval' : intervalInMinutes,
            'since' : past.timestamp()
        }
        postdata = urlencode(data)
        body = postdata.encode("utf-8")

        # -- API request --
        try:
            request = Request(self.URL, data=body)
        except HTTPError:
            if self.ping():
                raise 'cannot establish connection to kraken API, but server is up'
            else:
                raise 'lost connection to kraken API'
        except Exception as e:
            raise e

        # -- validate response --
        ticket = urllib.request.urlopen(request)
        raw_data = ticket.read()
        encoding = ticket.info().get_content_charset('utf8') # JSON default
        errors = json.loads(raw_data.decode(encoding))['error']  # return ticket result
        result = json.loads(raw_data.decode(encoding))['result']
        serverTimestamp = result['last'] # get server time to sync
        serverTime = datetime.fromtimestamp(serverTimestamp)
        timeseries = result[list(result.keys())[0]]
        past = serverTime - timedelta(minutes=epochInMinutes)
        if 'EService:Busy' in errors:
            raise 'kraken API service is busy'
        
        # -- build package --
        package = {
            'data': [],
            'length': len(timeseries),
            'pair': pair,
            'start': past.strftime("%m-%d-%y %H:%M:%S"),
            'startStamp': past.timestamp(),
            'stop': serverTime.strftime("%m-%d-%y %H:%M:%S"),
            'stopStamp': serverTimestamp,
        }
        for value in timeseries:
            dataPoint = [ # time/o/h/l/c/avg/volume
                datetime.fromtimestamp(value[0]).strftime("%m-%d-%y %H:%M:%S"),
                value[1],
                value[2],
                value[3],
                value[4],
                value[5],
                value[6]
            ] 
            package['data'].append(dataPoint)

        return package

    def ping(self):
        '''
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        '''
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '1', self.URL]
        return subprocess.call(command) == 0


if __name__ == '__main__':
    api = kraken()
    #print(api.OHLC('XRPEUR', 5, 1440))
    print(api.coins())

























