import json

file_path = '../assets/fido2_support.json'

def update_fido2_support_json(domain, login_urls, support_urls):
    with open(file_path, 'r') as file1:
        data = json.load(file1)

        if domain not in data:
            data[domain] = {
                'login_urls': [],
                'support_urls': []
            }

        for login_url in login_urls:
            if login_url not in data[domain]['login_urls']:
                data[domain]['login_urls'].append(login_url)

        for support_url in support_urls:
            if support_url not in data[domain]['support_urls']:
                data[domain]['support_urls'].append(support_url)

    with open(file_path, 'w') as file2:
        json.dump(data, file2, indent=4)