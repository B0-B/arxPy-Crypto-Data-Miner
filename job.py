from arxPy.tools import *
from arxPy.api import server, handler
from time import sleep

# -- slicing parameters --
port = 8080
intervalInMinutes = 5
epochInMinutes = 24*60
dataBasePath = './data/ohlc.db'
baseCurrency = 'USD'
arxiveTime = '00:00'


if __name__ == '__main__':

    log('start...', 'y')

    # build modules
    log('load modules ...')
    arx = arxive(dataBasePath)
    krk = kraken()

    # invoke server
    log(f'invoke rest API server at http://localhost:{port}', 'y')
    api = server(port, handler)
    api.httpd.serve_forever()

    # aggregate
    while False:

        try:
            
            if krk.ping():
                log('Try to reach kraken ...', 'y')
                log('kraken is up!', 'g')
                log('connect to db ...')
                for coin in krk.coins():
                    try:
                        log(f'archiving {coin} dataframe ...\r')
                        sleep(.3)
                        
                        # request pkg
                        pkg = krk.OHLC(coin+baseCurrency, intervalInMinutes, epochInMinutes)
                        arx.addPair(coin+baseCurrency) # creates new table for pair
                        arx.appendPackage(pkg)
                    except Exception as e:
                        log(f'Cannot draw data for {coin}, skip...', 'r')
                
                log('sleep mode zZz...')
                sleep(60*epochInMinutes)
            
            else:

                log('kraken not responding, will try again soon ...', 'r')
                sleep(1200)

        except KeyboardInterrupt:
            log('interupted.', 'y')
            arx.close() # close db session
            exit(0)
        except Exception as e:
            log('Error occured, pausing for 5 seconds ...', 'r')
            sleep(5)