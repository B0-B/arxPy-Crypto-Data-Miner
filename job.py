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
    api = kraken()

    while True:

        try:
            
            if api.ping():

                log('kraken is up!', 'g')
                
                for coin in api.coins():
                    log(f'archiving {coin} dataframe ...\r')
                    sleep(.01)
                    
                    # request pkg
                    pkg = api.OHLC(coin+baseCurrency, intervalInMinutes, epochInMinutes)
                    arx.addPair(coin+baseCurrency)
                    arx.appendPackage(pkg)

                
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
            log(e, 'r')
            log('Error occured, pausing for 5 minutes ...', 'r')
            sleep(300)
            
