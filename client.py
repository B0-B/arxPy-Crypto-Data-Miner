from arxPy.client import client

HOST = 'http://localhost'
PORT = 8080

# load arxpy client which connects to HOST API
arx = client(HOST, PORT)

# request OHLC time frame
ethTimeFrame = arx.timeFrameData('XETHZUSD', '07-31-21 20:25', '07-31-21 23:35') 
btcTimeFrame = arx.timeFrameData('TBTCUSD', '07-31-21 20:25', '07-31-21 23:35') 
# ...

print('ETH\n', ethTimeFrame)
print('BTC\n', btcTimeFrame)