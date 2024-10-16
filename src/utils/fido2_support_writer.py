import json
import os

file_path = '../assets/fido2_support.json'

def add_unique_urls(existing_urls, new_urls):
    existing_set = set(existing_urls)
    existing_set.update(new_urls)
    return list(existing_set)

def update_fido2_support_json(domain, login_urls, support_urls, yubikey, sso_archive):
    if not os.path.exists(file_path):
        data = {}
    else:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[fido2_support_writer] Error reading {file_path}: {e}")
            return

    if domain not in data:
        data[domain] = {
            'login_urls': [],
            'support_urls': [],
            ['yubikey']: {
                'yubikey_url': [],
                'fido_support': False,
            },
            ['sso_archive']: {
                'fido_configuration': False,
                'fido_2fa_configuration': False,
                'fido2_configuration': False,
            }
        }

    data[domain]['login_urls'] = add_unique_urls(data[domain]['login_urls'], login_urls)
    data[domain]['support_urls'] = add_unique_urls(data[domain]['support_urls'], support_urls)

    data[domain]['yubikey']['yubikey_url'] = add_unique_urls(data[domain]['yubikey']['yubikey_url'], yubikey.get('yubikey_url', []))
    data[domain]['yubikey']['fido_support'] = yubikey.get('fido_support')

    data[domain]['sso_archive']['fido_configuration'] = sso_archive.get('fido_configuration')
    data[domain]['sso_archive']['fido_2fa_configuration'] = sso_archive.get('fido_2fa_configuration')
    data[domain]['sso_archive']['fido2_configuration'] = sso_archive.get('fido2_configuration')

    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"[fido2_support_writer] Error writing to {file_path}: {e}")
