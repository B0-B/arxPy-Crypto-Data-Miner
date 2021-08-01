# modules
import os
import json
import urllib
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
from datetime import datetime, timedelta
import sqlite3
from sqlite3 import Error as SQLError



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
                datetime.fromtimestamp(value[0]).strftime("%m-%d-%y %H:%M"),
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
        command = ['ping', param, '1', 'api.kraken.com']
        return subprocess.call(command) == 0


class arxive:
    
    def __init__(self, path):
        self.PATH = path
        # open SQL session
        try:
            self.session = sqlite3.connect(self.PATH)
            self.cursor = self.session.cursor()
        except SQLError as e:
            raise ConnectionError(f'cannot connect to data base:\n{e}')
    
    def addPair(self, pair):
        '''
        For each pair create a seperate table.
        '''
        self.connect()
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {pair} (time text, o FLOAT(32), h FLOAT(32), l FLOAT(32), c FLOAT(32), a FLOAT(32), v FLOAT(32))"""
        )
        self.close()

    def appendPackage(self, package):
        '''
        A timeseries package will automatically be sorted into correct table
        '''
        self.connect()
        for d in package['data']:
            cmd = f"""INSERT INTO {package['pair']}\nVALUES ("{d[0]}", {d[1]}, {d[2]}, {d[3]}, {d[4]}, {d[5]}, {d[6]})"""
            self.cursor.execute(cmd)
        self.close()
    
    def close(self):
        self.session.close()

    def connect(self):
        self.session = sqlite3.connect(self.PATH)
    
    def query(self, tableName, *keys):
        self.connect()
        cmd = f'''SELECT {', '.join([f'"{k}"' for k in keys])} from {tableName}'''
        try:
            self.cursor.execute(cmd)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.note(e, logType='DATABASE ERROR', fTree=True, logTypeCol='\033[91m')
        finally:
            self.close()

    def queryRow(self, tableName, key, value):
        try:
            self.connect()
            self.cursor.execute(f'''SELECT * from {tableName} where "{key}"="{value}"''')
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.note(e, logType='DATABASE ERROR', fTree=True, logTypeCol='\033[91m')
        finally:
            self.close()

def log (output, color='w', label='arxPy'):
    if color == 'r':
        color = '\033[0;31m'
    elif color == 'y':
        color = '\033[0;33m'
    elif color == 'g':
        color = '\033[0;32m'
    else:
        color = ''
    print(f'[{label}]   {color}{output}\033[0m')


    

























