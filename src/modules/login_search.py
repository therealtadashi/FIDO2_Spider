import copy
import ssl
import urllib
from collections import deque
from copy import deepcopy
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


def extract_url_from_href(href, domain):
    url = https + domain
    if https in href:
        start_index = href.find(https)
        url = href[start_index:]
    elif href.startswith('/'):
        url = url + href
    return url


def verify_root_domain(url, domain):
    extracted = tldextract.extract(url)
    root_domain = f'{extracted.domain}.{extracted.suffix}'
    return domain in root_domain


def scan_new_links_for_scripts(new_links):
    file_dict = {}
    for new_link in new_links:
        html = requests.get(new_link).text
        soup = BeautifulSoup(html, 'html.parser')
        files = get_scripts(soup)
        file_dict = scan_scripts(new_link, files)
    return file_dict


class LoginPageScraper:
    def __init__(self):
        self.to_visit = []
        self.visited = []
        self.potential_login = []
        self.potential_support_files = []
        self.rp = robotparser.RobotFileParser()
        yesterday = (datetime.now() - timedelta(days = 7)).strftime('%Y-%m-%d')
        self.datas = get_list(yesterday, '1', '1000')
        self.all_domain_names = [entry['domain'] for entry in self.datas]
        self.session = requests.Session()


    # check existence of common login path patterns
    def search_common_login_path_for_url(self, domain):
        print(f'[login_search] search for login path patterns for url: {domain}')

        base_url = self.check_connection_with_domain(domain)
        if base_url is None:
            return [], []
        self.set_up_login_search(base_url)
        login_urls = get_login_page_by_domain(domain, self.all_domain_names, self.datas)

        # TODO implement a working proxy rotation
        # TODO potential async requests

        if len(login_urls) == 0:
            print(f'[login_search] login page not found for url: {domain}')
            self.iterate_url_search_new_url(domain)
        else:
            for login_url in login_urls:
                print(f'[login_search] login page found with url: {login_url}')
                # scan_new_links_for_scripts(login_urls) # scan login url fron archive for fido support
                if self.can_fetch_url(login_url):
                    new_links = find_login_page(login_url)
                    # TODO move scanning to a specific implementation
                    file_dict = scan_new_links_for_scripts(new_links)
                    self.update_potential_login_list(login_url, file_dict)

        copy_login = list(set(deepcopy(self.potential_login)))
        copy_support = list(set(deepcopy(self.potential_support_files)))

        self.potential_login.clear()
        self.potential_support_files.clear()

        return copy_login, copy_support


    def send_requests_extract_new_urls(self, url, domain):
        try:
            html = self.session.get(url) # changed from requests.get
            status_code = html.status_code
            if status_code == 200:
                print(f'[login_search] valid path for url: {url}')

                html = html.text
                soup = BeautifulSoup(html, 'html.parser')
                self.find_new_links(soup, domain)  # searches for new links that is not in visited and not in to_visit
                new_links = find_login_page(url) # simulates login button interaction
                file_dict = scan_new_links_for_scripts(new_links)
                self.update_potential_login_list(url, file_dict)
            else:
                print(f'[login_search] invalid path for url {url} with status code {status_code}')

        except Exception as e:
            print(f'[login_search] Error finding login page for {url}: {e}')


    def set_up_robotsparser(self, base_url):
        robots_url = urljoin(base_url, robots)
        self.rp.set_url(robots_url)
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        try:
            with urllib.request.urlopen(robots_url, context=ssl_context) as response:
                self.rp.parse(response.read().decode('utf-8'))
                print(f'[login_search] Successfully read {robots_url}')
        except Exception as e:
            print(f'[login_search] Error reading {robots_url}: {e}')


    def can_fetch_url(self, url_to_check):
        return self.rp.can_fetch("*", url_to_check)


    def get_allowed_url_patterns(self):
        patterns = copy.deepcopy(path_patterns)
        allowed_url_patterns = [url for url in patterns if self.can_fetch_url(url)]
        return allowed_url_patterns


    def create_common_path_urls(self, base_url):
        allowed = self.get_allowed_url_patterns()
        for pattern in allowed:
            full_url = base_url + pattern
            self.to_visit.append(full_url)


    def find_new_links(self, soup, domain):
        for link in soup.find_all('a', href=True):
            href = link['href']
            url = extract_url_from_href(href, domain)
            if self.verify_url(url, domain):
                self.to_visit.append(url)


    def is_new_unvisited_link(self, link):
        return link not in self.to_visit


    def verify_url(self, url, domain):
        return verify_root_domain(url, domain) and self.can_fetch_url(url) and self.is_new_unvisited_link(url)


    def append_new_links(self, new_links):
        for new_link in new_links:
            if self.can_fetch_url(new_link) and self.is_new_unvisited_link(new_link):
                self.to_visit.append(new_link)


    def iterate_url_search_new_url(self, domain):
        # TODO to_visit to queue
        queue = deque(self.to_visit)
        while queue:
            url = queue.popleft()
            self.send_requests_extract_new_urls(url, domain)
            self.visited.append(url)


    def set_up_login_search(self, base_url):
        self.set_up_robotsparser(base_url)
        self.create_common_path_urls(base_url) # appends new_urls to to_visit

    def update_potential_login_list(self, login_url, file_dict):
        for file, support in file_dict.items():
            if support and file:
                self.potential_support_files.append(file)
                self.potential_login.append(login_url)


    def check_connection_with_domain(self, domain):
        print(f'[login_search] checking connection for domain {domain}')
        url = https + domain
        try:
            requests.get(url)
        except Exception as e:
            print(f'[login_search] domain {domain} cannot be reached {e}')
            url = get_url_for_domain(domain, self.all_domain_names, self.datas)
        return url