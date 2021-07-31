from arxPy.tools import *
from time import sleep

# -- slicing parameters --
intervalInMinutes = 5
epochInMinutes = 24*60
dataBasePath = './data/ohlc.db'
baseCurrency = 'USD'


if __name__ == '__main__':

    log('start...', 'y')

    # build modules
    log('load modules ...')
    arx = arxive(dataBasePath)
    krk = kraken()
    api = api('8000')

    while True:

        try:
            
            if krk.ping():

                log('kraken is up!', 'g')
                log('connect to db ...')
                arx.connect()
                for coin in krk.coins():
                    try:
                        log(f'archiving {coin} dataframe ...\r')
                        sleep(1)
                        
                        # request pkg
                        pkg = krk.OHLC(coin+baseCurrency, intervalInMinutes, epochInMinutes)
                        arx.addPair(coin+baseCurrency) # creates new table for pair
                        arx.appendPackage(pkg)
                        arx.close()
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
            
