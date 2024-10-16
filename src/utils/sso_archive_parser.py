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
        login_urls = []
        for login_url in login:
            login_urls.append(login_url.get(candidate))
        return list(set(login_urls))


def get_list(date, start, end):
    print(f'[sso_archive_parser] getting sso-archive list from {date}')
    try:
        archive_api = f'http://sso-monitor.me/api/list/?date={date}&start_rank={start}&end_rank={end}'
        response = requests.get(archive_api).text
        data = json.loads(response)
        return data
    except Exception as e:
        print(f'[sso_archive_parser] Error retrieving sso-archive: {e}')


def get_url_for_domain(domain_name, all_domain, data):
    domain_info = get_domain_info(domain_name, all_domain, data)
    if domain_info is None:
        return None
    else:
        resolved = domain_info.get('resolved', [])
        return resolved.get('url')


def get_fido_info_for_domain(domain_name, all_domain, data):
    print(f'[sso_archive_parser] searching for FIDO2 on sso-archive for the domain {domain_name}')
    domain_info = get_domain_info(domain_name, all_domain, data)
    if domain_info is None:
        return None
    else:
        fido_info = domain_info.get('metadata_available')
        sso_archive = {
            'fido_configuration': fido_info.get('fido_configuration'),
            'fido_2fa_configuration': fido_info.get('fido_2fa_configuration'),
            'fido2_configuration': fido_info.get('fido2_configuration')
        }
        return sso_archive