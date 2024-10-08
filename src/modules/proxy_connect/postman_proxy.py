import requests

proxy_api = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=all'
valid_proxies = ['5.42.83.51:3128', '72.10.160.90:16523', '72.10.164.178:25823', '67.43.228.253:31743', '15.235.153.57:8089', '72.10.164.178:2295', '67.43.227.228:7053', '72.10.160.174:25313', '72.10.164.178:24123', '5.189.130.42:23055', '190.121.145.115:999', '67.43.236.20:32043', '67.43.228.253:7929']

def get_valid_proxies():
    return valid_proxies

def get_postman_proxies():
    response = requests.get(proxy_api)
    proxies = response.text.splitlines()
    return proxies

def check_proxies():
    url = 'https://google.com'
    working_proxies = set()
    proxies = get_postman_proxies()
    for proxy in proxies:
        try:
            requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=10)
            working_proxies.add(proxy)
            print(proxy)
        except:
            continue
    return working_proxies