import json

import requests

candidates = 'login_page_candidates'
candidate = 'login_page_candidate'

def check_domain_in_archive(domain_name, all_domain):
    return domain_name in all_domain

def get_domain_info(domain_name, all_domain, data):
    if not check_domain_in_archive(domain_name, all_domain):
        return None
    for entry in data:
        if entry['domain'] == domain_name:
            return entry
    return None

def get_login_page_by_domain(domain_name, all_domain, data):
    domain_info = get_domain_info(domain_name, all_domain, data)
    if domain_info is None:
        return None
    else:
        login = domain_info.get(candidates, [])
        if len(login) > 0:
            return login[0].get(candidate)
    return None

def get_list(date, start, end):
    print(f'[sso_archive_parser] getting sso-archive list from {date}')
    archive_api = f'http://sso-monitor.me/api/list/?date={date}&start_rank={start}&end_rank={end}'
    response = requests.get(archive_api).text
    data = json.loads(response)
    return data