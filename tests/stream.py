import configparser
import asyncio
import time
import requests
from binance_chain.websockets import BinanceChainSocketManager
from binance_chain.environment import BinanceEnvironment

config = configparser.ConfigParser()
config.read('./stream.conf')

loop = None
bnb_webhook_url = config['stream']['bnb_webhook_url']
token = config['stream']['bnb_token']
address = config.get('stream', 'bnb_master_address').strip()
bnb_api_url = config['stream']['bnb_api_url']
bnb_wss_url = config['stream']['bnb_wss_url']
bnb_hrp_url = config['stream']['bnb_hrp_url']
use_testnet = config['stream'].getboolean('use_testnet')
sleep_time = config['stream'].getint('sleep_time')

if use_testnet is True:
    print("Use test net")
    testnet_env = BinanceEnvironment.get_testnet_env()
else:
    print('Use main net')
    testnet_env = BinanceEnvironment(api_url=bnb_api_url, wss_url=bnb_wss_url, hrp=bnb_hrp_url)

print('bnb_webhook_url: {}, token: {}, address: {}'.format(bnb_webhook_url, token, str(address)))
print('bnb_api_url: {}, bnb_wss_url: {}, bnb_hrp_url: {}'.format(bnb_api_url, bnb_wss_url, bnb_hrp_url))
headers = {
    'content-type': 'application/json',
    'Authorization': '',
}

async def main():
    global loop

    async def handle_evt(msg):
        """Function to handle websocket messages
        """
        try:
            requests.post(bnb_webhook_url, params={'token': token}, json=msg, headers=headers)
        except Exception as ex :
            pass
          
    # connect to environment
    bcsm = await BinanceChainSocketManager.create(loop, handle_evt, env=testnet_env)
    # subscribe to relevant endpoints
    await bcsm.subscribe_transfers(address=address)
    
    while True:
        print("Sleeping to keep loop open")
        await asyncio.sleep(sleep_time, loop=loop)

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
