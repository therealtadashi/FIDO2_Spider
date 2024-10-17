import requests


credentials = 'navigator.credentials'

def get_scripts(soup):
    scripts = soup.find_all('script')
    js_files = [script.get('src') for script in scripts if 'src' in script.attrs]
    return js_files


def scan_scripts(url, js_files):
    file_dict = {}
    for js_file in js_files:
        if js_file.startswith('/'):
            js_file = url + js_file
        js_response = requests.get(js_file)
        text = js_response.text

        if f'{credentials}.create' in text or f'{credentials}.get' in text:
            print(f"[fido2_support] {credentials} detected in {js_file}, possible FIDO2 implementation")
            file_dict[js_file] = True
        else:
            print(f'[fido2_support] no sign of FIDO2 found in {js_file}')
            file_dict[js_file] = False
    return file_dict


def scan_well_known(url):
    url = f'https://{url}/.well-known/'
    well_known = {
        'url': url,
        'support': False
    }
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f'[fido2_support] .well-known found at {url}')
            well_known = {
                'url': url,
                'support': True
            }
            return well_known
    except Exception as e:
        print(f'[fido2_support] Exception while visiting {url}: {e}')
    return well_known