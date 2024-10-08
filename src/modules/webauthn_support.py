import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def supports_fido2_webauthn(url):
    try:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        if "navigator.credentials.create" in driver.page_source or "PublicKeyCredential" in driver.page_source:
            print(f"[webauthn_support] FIDO2/WebAuthn supported on {url}")
            driver.quit()
            return True
        else:
            print(f"[webauthn_support] FIDO2/WebAuthn not found on {url}")
            driver.quit()
            return False
    except Exception as e:
        print(f"[webauthn_support] Error checking FIDO2/WebAuthn for {url}: {e}")


def search_for_authn(soup):
    if 'navigator.credentials.create' in soup.text or 'navigator.credentials.get' in soup.text:
        print("[webauthn_support] Page likely supports WebAuthn")
        return True

    if 'Use Security Key' in soup.text or 'Passwordless Login' in soup.text:
        print('[webauthn_support] Page likely supports WebAuthn')
        return True

    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('webauthn' in script.string.lower() or 'publickeycredential' in script.string):
            print('[webauthn_support] Custom WebAuthn script detected')
            return True
    print('[webauthn_support] WebAuthN Search finished')
    return False