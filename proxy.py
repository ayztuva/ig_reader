from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
import requests

URL_TST = 'https://stackoverflow.com/'
URL_IG = 'https://stackoverflow.com/'
URL_PX = 'https://free-proxy-list.net/'


def get_proxy():
    proxies = []
    html = requests.get(URL_PX).text
    soup = BeautifulSoup(html, 'lxml')

    trs = soup.find('table', id='proxylisttable').find_all('tr')[1:21]
    
    while not proxies:
        for tr in trs:
            tds = tr.find_all('td')
            if tds[-2].text.strip() == 'yes':
                ip = tds[0].text
                port = tds[1].text
                country = tds[3].text
                data = {
                    'schema': 'https',
                    'address': f'{ip}:{port}',
                    'country': country
                }
                proxies.append(data)
        
        if not proxies:
            print('---\tNo HTTPS proxies. Retry in 5 minutes.')
            sleep(300)
        elif len(proxies) < 2:
            print(f'---\tNot enough HTTPS proxies ({len(proxies)}).')
            print('\tRetry in 5 minutes.')
            proxies.clear()
            sleep(300)

    print(f'+++\tGot {len(proxies)} proxies - ready to work.')
    return proxies



def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    proxies = get_proxy()
    
    for p in proxies:
        proxy = f"{p['schema']}:{p['address']}"
        
        if len(options.arguments) > 1:
            options.arguments.pop()
        
        options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Firefox(options=options)
        try:
            driver.get(URL_IG)
            print(driver.current_url)
        except Exception as e:
            print('---\tBad proxy.')
            print(f'\t{e}')
        driver.quit()

if __name__ == '__main__':
    main()
