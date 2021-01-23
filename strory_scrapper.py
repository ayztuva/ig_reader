"""
"""
import os

import requests
from selenium import webdriver
from bs4 import BeautifulSoup

from tools.proxy import Proxy

TOKEN = os.getenv('PROXY_STORE_KEY')


def get_proxy(proxies):
    if proxies:
        for proxy in proxies:
            yield proxy
    return None

def check_url(url):
    pass

def main():
    proxies = Proxy(TOKEN)

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--proxy-server=' + get_proxy(proxies.selenium_list))
    driver = webdriver.Firefox(options=options)

    url = input('URL: ')
    driver.get(url)
    soup = BeautifulSoup(driver.page_source)

    driver.quit()

if __name__ == '__main__':
    main()
