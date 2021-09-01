#!/usr/bin/env python3
from arxPy.tools import *
from arxPy.api import server, handler
from time import sleep

# -- slicing parameters --
port = 8080
aggregate = False
intervalInMinutes = 5
epochInMinutes = 24*60
dataBasePath = './data/ohlc.db'
baseCurrency = 'USD'
arxiveTime = '17:00'


if __name__ == '__main__':

    banner()
    log('start...', 'y')

    # -- instantiate modules --
    log('load modules ...')
    arx = arxive(dataBasePath)
    krk = kraken()

    # -- invoke uncoupled API background service --
    log(f'invoke rest API server at http://localhost:{port}', 'y')
    api = server(port, handler)
    api.invoke() # asynchronous thread

    # -- aggregate --
    if aggregate:
        log('scheduled aggregation at '+arxiveTime, 'g')
        while waitingForSchedule(arxiveTime): 
            clock()
            sleep(30)
    while True:

        try:

            if aggregate:

                # show clock
                clock()

                # first make sure that kraken API is reachable
                log('Try to reach kraken ...', 'y')
                while not krk.ping():
                    log('kraken not responding, will try again soon ...', 'r')
                    sleep(5)
                log('kraken is up!', 'g')

                # run the archiving
                log('connect to db ...')
                for coin in krk.coins():
                    try:
                        log(f'crawl and archive {coin} dataframe ...\r')
                        sleep(.3) # the one and only denial of service protection =)
                        
                        # request pkg
                        pkg = krk.OHLC(coin+baseCurrency, intervalInMinutes, epochInMinutes)
                        arx.addPair(coin+baseCurrency) # creates new table for pair
                        arx.appendPackage(pkg)
                    except Exception as e:
                        log(f'Cannot draw data for {coin}, skip...', 'r')
                
                # wait one epoch for next aggregation
                log('next aggregation at '+arxiveTime, 'g')
                while waitingForSchedule(arxiveTime): 
                    clock()
                    sleep(30)

        except KeyboardInterrupt:
            log('interupted.', 'y')
            arx.close() # close db session
            exit(0)
        except Exception as e:
            log('Error occured, pausing for 5 seconds ...', 'r')
            sleep(5)
