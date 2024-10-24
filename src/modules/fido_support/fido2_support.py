import time
import requests
from src.utils.set_up_driver import setup_driver

credentials = 'navigator.credentials'
conditionals = 'isConditionalMediationAvailable'
u2f = 'window.u2f'


def get_scripts(soup):
    scripts = soup.find_all('script')
    js_files = [script.get('src') for script in scripts if 'src' in script.attrs]
    return js_files


import requests

def scan_scripts(url, js_files):
    file_dicts = []
    processed_paths = set()

    for js_file in js_files:
        if js_file.startswith('/'):
            js_file = url + js_file
        if js_file in processed_paths:
            continue
        js_response = requests.get(js_file)
        text = js_response.text
        file_dict = {'path': js_file}
        if f'{credentials}.create' in text or f'{credentials}.get' in text:
            print(f'[fido2_support] {credentials} detected in {js_file}')
            file_dict[credentials] = True
        else:
            file_dict[credentials] = False
        if conditionals in text:
            print(f'[fido2_support] {conditionals} detected in {js_file}')
            file_dict[conditionals] = True
        else:
            file_dict[conditionals] = False
        if "require('u2f-api')" in text or 'window.u2f.sign()' in text:
            print(f'[fido2_support] u2f detected in {js_file}')
            file_dict['u2f'] = True
        else:
            file_dict['u2f'] = False
        processed_paths.add(js_file)
        file_dicts.append(file_dict)
    return file_dicts



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
    try:
        driver.get(url)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setRequestInterception", {
            "patterns": [{"urlPattern": "*"}]
        })
        while True:
            try:
                intercepted_event = driver.execute_cdp_cmd("Network.getRequestPostData", {})
                if intercepted_event:
                    interception_id = intercepted_event["interceptionId"]
                    request_headers = intercepted_event["headers"]
                    print(f"Intercepted Request Headers: {request_headers}")
                    driver.execute_cdp_cmd("Network.continueInterceptedRequest", {
                        "interceptionId": interception_id,
                        "headers": {
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
                        }
                    })
                    break
            except Exception as e:
                print(f"Waiting for intercepted request...: {e}")
            time.sleep(1)
    except Exception as e:
        print(f"Error during interception: {str(e)}")
    finally:
        driver.quit()