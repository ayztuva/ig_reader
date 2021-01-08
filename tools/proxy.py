"""
Proxy-Store api documentation: https://proxy-store.com/ru/developers
"""
import os
from time import sleep

import requests
from dotenv import load_dotenv

load_dotenv()
PROXY_KEY = os.getenv("PROXY_STORE_KEY")

HEADERS = {'User-Agent': 'Chrome'}
URL = 'https://www.instagram.com/'
PROXY_URL = f'https://proxy-store.com/api/{PROXY_KEY}/'


def get_proxies():
    """
    Returns list with proxies from https://proxy-store.com/.
    """
    proxies = []
    while True:
        response = requests.get(PROXY_URL + 'getproxy/').json()
        for p in response['list'].values():
            data = {
                'schema': p['type'],
                'address': p['ip'] + ':' + p['port']
            }
            proxy = {
                data['schema']: data['schema'] + '://' + data['address']
            }
            r = requests.get(
                URL,
                proxies=proxy,
                headers=HEADERS,
                timeout=5
            )
            if r.status_code == 200:
                proxies.append(data)
        if proxies:
            break
    return proxies


def change_proxy(proxies):
    """
    Chooses next proxy from given list.
    If list is empty, waits for hour and returns proxies list.
    """
    print('===\tChanging proxy.')
    try:
        proxy = proxies.pop()
    except IndexError:
        print(
            '===\tRun out of proxies. Has to wait for one hour and repeat.')
        minutes = 60
        while minutes > 0:
            print(f'Time left:\t{minutes} min.')
            minutes -= 5
            sleep(300)
        proxies.extend(get_proxies())
        proxy = proxies.pop()
    return proxy


if __name__ == '__main__':
    get_proxies()
