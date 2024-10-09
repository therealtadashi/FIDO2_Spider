import requests

def get_scripts(soup):
    scripts = soup.find_all('script')
    js_files = [script.get('src') for script in scripts if 'src' in script.attrs]
    return js_files

def scan_scripts(url, js_files):
    for js_file in js_files:
        if js_file.startswith('/'):
            js_file = url + js_file
        js_response = requests.get(js_file)

        if 'navigator.credentials.create' in js_response.text or 'navigator.credentials.get' in js_response.text:
            print(f"[fido2_support] navigator.credentials detected in {js_file}, possible FIDO2 implementation")
        else:
            print(f'[fido2_support] no sign of FIDO2 found in {js_file}')

def scan_well_known(url):
    try:
        well_known = url + '/.well-known/fido2-configuration'
        response = requests.get(well_known)
        if response.status_code == 200:
            print(f'[fido2_support] .well-known found at {well_known}')
    except Exception as e:
        print(f'[fido2_support] Exception while visiting {url}: {e}')
