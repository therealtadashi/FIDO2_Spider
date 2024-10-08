import copy
import ssl
import urllib
from datetime import datetime, timedelta
from urllib import robotparser
from urllib.parse import urljoin
import certifi
import tldextract
import requests
from bs4 import BeautifulSoup
from src.modules.user_interaction.simulate_user_interaction import find_login_page
from src.utils.csv_url_reader import read_url
from src.utils.sso_archive_parser import get_login_page_by_domain, get_list

path_patterns = ['/account', '/accounts', '/login', '/signin', '/user', '/auth'] # common patterns for login paths
base_url = read_url()[4] # first elem in the tranco list
robots = '/robots.txt' # robots.txt path
https = 'https://'

rp = robotparser.RobotFileParser()
yesterday =  (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
datas = get_list(yesterday, '1', '1000')
all_domain_names = [entry['domain'] for entry in datas]

to_visit = []
visited = []


def send_request_to_tranco_url():
    print(f'[login_search] sending request to: {base_url}')
    html = requests.get(https + base_url).text
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)

# check existence of common login path patterns
def search_common_login_path_for_url():
    print(f'[login_search] search for login path patterns for url: {base_url}')

    set_up_robotsparser()
    common_path_urls() # appends new_urls to to_visit
    login_url = get_login_page_by_domain(base_url, all_domain_names, datas)
    # TODO implement a working proxy rotation

    if login_url is None:
        print(f'[login_search] login page not found for url: {base_url}')
        iterate_url_search_new_url()
    else:
        print(f'[login_search] login page found with url: {login_url}')
        find_login_page(login_url)

    print(visited)


def send_requests_extract_new_urls(url):
    try:
        html = requests.get(url)
        status_code = html.status_code
        if status_code == 200:
            print(f'[login_search] valid path for url: {url}')

            html = html.text
            soup = BeautifulSoup(html, 'html.parser')
            find_new_links(soup)  # searches for new links that is not in visited and not in to_visit
            new_links = find_login_page(url) # simulates button interaction and searches new links
            append_new_links(new_links)
            # TODO detect support and change return val
            # supports_fido = supports_fido2_webauthn(url) # check if page potentially supports FIDO2
            return url, False
        else:
            print(f'[login_search] invalid path for url {url} with status code {status_code}')
            return url, False

    except Exception as e:
        print(f'[login_search] Error finding login page for {url}: {e}')


def set_up_robotsparser():
    robots_url = urljoin(https + base_url, robots)
    rp.set_url(robots_url)
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        with urllib.request.urlopen(robots_url, context=ssl_context) as response:
            rp.parse(response.read().decode('utf-8'))
            print(f'[login_search] Successfully read {robots_url}')
    except Exception as e:
        print(f'[login_search] Error reading {robots_url}: {e}')


def can_fetch_url(url_to_check):
    return rp.can_fetch("*", url_to_check)


def get_allowed_url_patterns():
    patterns = copy.deepcopy(path_patterns)
    allowed_url_patterns = [url for url in patterns if can_fetch_url(url)]
    return allowed_url_patterns


def common_path_urls():
    allowed = get_allowed_url_patterns()
    for pattern in allowed:
        full_url = https + base_url + pattern
        to_visit.append(full_url)


def find_new_links(soup):
    for link in soup.find_all('a', href=True):
        href = link['href']
        url = extract_url_from_href(href)
        if verify_url(url):
            to_visit.append(url)


def extract_url_from_href(href):
    url = https + base_url
    if https in href:
        start_index = href.find(https)
        url = href[start_index:]
    elif href.startswith('/'):
        url = url + href
    return url


def is_new_unvisited_link(link):
    return link not in to_visit


def verify_root_domain(url):
    extracted = tldextract.extract(url)
    root_domain = f'{extracted.domain}.{extracted.suffix}'
    return base_url in root_domain


def verify_url(url):
    return verify_root_domain(url) and can_fetch_url(url) and is_new_unvisited_link(url)


def append_new_links(new_links):
    for new_link in new_links:
        if can_fetch_url(new_link) and is_new_unvisited_link(new_link):
            to_visit.append(new_link)


def iterate_url_search_new_url():
    for url in to_visit:
        url, supports_fido = send_requests_extract_new_urls(url)
        # TODO handle supports_fido
        to_visit.remove(url)
        visited.append(url)
