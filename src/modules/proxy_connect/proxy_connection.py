import requests
from bs4 import BeautifulSoup

# free proxy database
# proxy_url = 'https://spys.one/en/free-proxy-list/'
proxy_url = 'https://free-proxy-list.net/'

def get_proxies():
    response = requests.get(proxy_url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    containers = soup.find_all('div', {'class': 'table-responsive'})[0]
    ip_index = [8*k for k in range(80)]
    proxies = set()

    for i in ip_index:
        ip = containers.find_all('td')[i].text
        port = containers.find_all('td')[i+1].text
        https = containers.find_all('td')[i+6].text
        if https == 'yes':
            proxy = f'{ip}:{port}'
            proxies.add(proxy)

    return proxies

def check_proxies():
    url = 'https://google.com'
    working_proxies = set()
    proxies = get_proxies()
    for proxy in proxies:
        try:
            requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=10)
            working_proxies.add(proxy)
        except:
            continue
    return working_proxies