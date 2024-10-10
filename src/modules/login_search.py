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
from src.modules.fido_support.fido2_support import get_scripts, scan_scripts
from src.modules.user_interaction.simulate_user_interaction import find_login_page
from src.utils.sso_archive_parser import get_login_page_by_domain, get_list, get_url_for_domain

path_patterns = ['/account', '/accounts', '/login', '/signin', '/user', '/auth'] # common patterns for login paths
robots = '/robots.txt' # robots.txt path
https = 'https://'

rp = robotparser.RobotFileParser()
yesterday =  (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
datas = get_list(yesterday, '1', '1000')
all_domain_names = [entry['domain'] for entry in datas]

to_visit = []
visited = []
potential_login = []
potential_support_files = []

#TODO create LoginPageScraperClass

# check existence of common login path patterns
def search_common_login_path_for_url(domain):
    print(f'[login_search] search for login path patterns for url: {domain}')

    base_url = check_connection_with_domain(domain)
    if base_url is None:
        return [], []
    set_up_login_search(base_url)
    login_urls = get_login_page_by_domain(domain, all_domain_names, datas)
    # TODO implement a working proxy rotation
    # TODO potential async requests
    if len(login_urls) == 0:
        print(f'[login_search] login page not found for url: {domain}')
        iterate_url_search_new_url(domain)
    else:
        for login_url in login_urls:
            print(f'[login_search] login page found with url: {login_url}')
            # scan_new_links_for_scripts(login_urls) # scan login url for fido support
            if can_fetch_url(login_url):
                new_links = find_login_page(login_url)
                file_dict = scan_new_links_for_scripts(new_links)
                update_potential_login_list(login_url, file_dict)

    return list(set(potential_login)), list(set(potential_support_files))


def send_requests_extract_new_urls(url, domain):
    try:
        html = requests.get(url)    # TODO session.get(url)
        status_code = html.status_code
        if status_code == 200:
            print(f'[login_search] valid path for url: {url}')

            html = html.text
            soup = BeautifulSoup(html, 'html.parser')
            find_new_links(soup, domain)  # searches for new links that is not in visited and not in to_visit
            new_links = find_login_page(url) # simulates login button interaction
            file_dict = scan_new_links_for_scripts(new_links)
            update_potential_login_list(url, file_dict)
        else:
            print(f'[login_search] invalid path for url {url} with status code {status_code}')

    except Exception as e:
        print(f'[login_search] Error finding login page for {url}: {e}')


def set_up_robotsparser(base_url):
    robots_url = urljoin(base_url, robots)
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


def create_common_path_urls(base_url):
    allowed = get_allowed_url_patterns()
    for pattern in allowed:
        full_url = base_url + pattern
        to_visit.append(full_url)


def find_new_links(soup, domain):
    for link in soup.find_all('a', href=True):
        href = link['href']
        url = extract_url_from_href(href, domain)
        if verify_url(url, domain):
            to_visit.append(url)


def extract_url_from_href(href, domain):
    url = https + domain
    if https in href:
        start_index = href.find(https)
        url = href[start_index:]
    elif href.startswith('/'):
        url = url + href
    return url


def is_new_unvisited_link(link):
    return link not in to_visit


def verify_root_domain(url, domain):
    extracted = tldextract.extract(url)
    root_domain = f'{extracted.domain}.{extracted.suffix}'
    return domain in root_domain


def verify_url(url, domain):
    return verify_root_domain(url, domain) and can_fetch_url(url) and is_new_unvisited_link(url)


def append_new_links(new_links):
    for new_link in new_links:
        if can_fetch_url(new_link) and is_new_unvisited_link(new_link):
            to_visit.append(new_link)


# TODO to_visit to que
def iterate_url_search_new_url(domain):
    for url in to_visit:
        send_requests_extract_new_urls(url, domain)
        to_visit.remove(url)
        visited.append(url)


def set_up_login_search(base_url):
    set_up_robotsparser(base_url)
    create_common_path_urls(base_url) # appends new_urls to to_visit


def scan_new_links_for_scripts(new_links):
    file_dict = {}
    for new_link in new_links:
        html = requests.get(new_link).text
        soup = BeautifulSoup(html, 'html.parser')
        files = get_scripts(soup)
        file_dict = scan_scripts(new_link, files)
    return file_dict


def update_potential_login_list(login_url, file_dict):
    for file, support in file_dict.items():
        if support and file:
            potential_support_files.append(file)
            potential_login.append(login_url)


def check_connection_with_domain(domain):
    print(f'[login_search] checking connection for domain {domain}')
    url = https + domain
    try:
        requests.get(url)
    except Exception as e:
        print(f'[login_search] domain {domain} cannot be reached {e}')
        url = get_url_for_domain(domain, all_domain_names, datas)
    return url