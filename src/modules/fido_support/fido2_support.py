import time
import requests
from src.utils.set_up_driver import setup_driver

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


def execute_script_api_support(url):
    driver = setup_driver()
    driver.get(url)
    time.sleep(3)
    webauthn_api = {}
    webauthn_supported = driver.execute_script(
        "return (typeof window.PublicKeyCredential !== 'undefined');"
    )
    credentials_create_supported = driver.execute_script(
        "return (typeof navigator.credentials !== 'undefined' && typeof navigator.credentials.create !== 'undefined');"
    )
    credentials_get_supported = driver.execute_script(
        "return (typeof navigator.credentials !== 'undefined' && typeof navigator.credentials.get !== 'undefined');"
    )

    webauthn_api[url] = {
        "public_key_credentials": webauthn_supported,
        "navigator_create": credentials_create_supported,
        "navigator_get": credentials_get_supported
    }

    return webauthn_api


def check_fido2_specific_headers(url):
    driver = setup_driver()
    driver.execute_cdp_cmd("Network.enable", {})
    driver.get(url)

    def capture_headers(request):
        headers = request['request']['headers']
        print(f"Request URL: {request['request']['url']}")
        print(f"Request Headers: {headers}")

    driver.execute_cdp_cmd("Network.setRequestInterception", {
        "patterns": [{"urlPattern": "*"}]
    })

    driver.execute_cdp_cmd("Network.requestIntercepted", {
        "interceptionId": "1",
        "params": capture_headers
    })

    driver.quit()