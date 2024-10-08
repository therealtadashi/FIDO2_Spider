import queue
import threading
import requests

q = queue.Queue()
valid_proxies = []

with open('../../../assets/proxy_list.txt', 'r') as f:
    proxies = f.read().split('\n')
    for proxy in proxies:
        q.put(proxy)

def check_proxies():
    global q
    while not q.empty():
        p = q.get()
        try:
            response = requests.get('https://google.com', proxies={'http': p, 'https': p})
        except:
            continue
        if response.status_code == 200:
            print(p)

for _ in range(10):
    threading.Thread(target=check_proxies).start()