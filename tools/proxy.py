"""
Proxy module.
Proxy-Store api documentation: https://proxy-store.com/ru/developers
"""
import requests

URL = 'https://proxy-store.com/api/{}/'


class Proxy:
    """
    Get private proxies from proxy-store.com.
    Return Proxy() object whitch contains:
    - unadaptive proxies list;
    - requests library adaptive proxies list;
    - selenium adaptive proxies list.
    Personal proxy-store token required.
    """
    def get_proxy(token):
        """Request to proxy-store.com."""
        response = requests.get(URL.format(token) + 'getproxy/').json()
        if response.get('status') == 'ok':
            return response.get('list')
        return []

    def __init__(self, token):
        """Unadaptive, requests and selenium adaptive proxies."""
        self.list = Proxy.get_proxy(token)
        self.requests_list = self.__adapt_to_requests()
        self.selenium_list = self.__adapt_to_selenium()

    def __adapt_to_requests(self):
        """Convert to requests lib. proxies."""
        requests_list = []
        for proxy in self.list.values():
            address = proxy['type'] + '://' + proxy['ip'] + ':' + proxy['port']
            requests_list.append({proxy['type']: address})
        return requests_list

    def __adapt_to_selenium(self):
        """Convert to selenium proxies."""
        selenium_list = []
        for proxy in self.list.values():
            address = proxy['type'] + ':' + proxy['ip'] + ':' + proxy['port']
            selenium_list.append(address)
        return selenium_list
