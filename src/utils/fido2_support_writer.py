import json
import os

file_path = '../assets/fido2_support.json'

def add_unique_urls(existing_urls, new_urls):
    existing_set = set(existing_urls)
    existing_set.update(new_urls)
    return list(existing_set)


def load_json():
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[fido2_support_writer] Error reading {file_path}: {e}")
            return {}
    return {}


def save_json(data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"[fido2_support_writer] Error writing to {file_path}: {e}")


def setup_json_structure(domain, data):
    if domain not in data:
        data[domain] = {
            'login_search': {
                'login_urls': [],
                'js_file_paths': [],
            },
            'cross_reference': {
                'sso_archive': {
                    'fido_configuration': False,
                    'fido_2fa_configuration': False,
                    'fido2_configuration': False,
                },
                'yubikey': {
                    'yubikey_url': [],
                    'fido_support': False,
                },
                'hideez': {
                    'hideez_block': {},
                    'fido_support': False,
                },
                'dongleauth': {},
            },
            'well_known': {
                'url': '',
                'support': '',
            },
        }


def update_login_search(domain, login_search):
    data = load_json()
    setup_json_structure(domain, data)
    login = data[domain]['login_search']

    login['login_urls'] = add_unique_urls(login['login_urls'], login_search['login_urls'])

    new_js_files = login_search['js_file_paths']
    existing_js_files = login['js_file_paths']
    existing_paths = {file['path'] for file in existing_js_files}

    for new_file in new_js_files:
        if new_file['path'] not in existing_paths:
            existing_js_files.append(new_file)

    save_json(data)


def update_cross_reference(domain, sso_archive, yubikey, hideez, dongleauth):
    data = load_json()
    setup_json_structure(domain, data)
    cross_reference = data[domain]['cross_reference']

    cross_reference['sso_archive']['fido_configuration'] = sso_archive.get('fido_configuration')
    cross_reference['sso_archive']['fido_2fa_configuration'] = sso_archive.get('fido_2fa_configuration')
    cross_reference['sso_archive']['fido2_configuration'] = sso_archive.get('fido2_configuration')

    cross_reference['yubikey']['yubikey_url'] = add_unique_urls(cross_reference['yubikey']['yubikey_url'], yubikey.get('yubikey_url', []))
    cross_reference['yubikey']['fido_support'] = yubikey.get('fido_support')

    cross_reference['hideez']['hideez_block'].update(hideez.get('hideez_block', {}))
    cross_reference['hideez']['fido_support'] = hideez.get('fido_support')

    cross_reference['dongleauth'].update(dongleauth)

    save_json(data)


def update_well_known(domain, well_known):
    data = load_json()
    setup_json_structure(domain, data)

    data[domain]['well_known']['url'] = well_known.get('url')
    data[domain]['well_known']['support'] = well_known.get('support')

    save_json(data)