import time
from selenium.webdriver.common.by import By
from src.modules.set_up_driver import setup_driver
from src.modules.user_interaction.cookie_interaction import handle_cookie_popup


def yubikey_catalog_fido2_cross_reference(domain):
    print(f'[webauthn_adoption] searching for FIDO2 on yubikey catalog for the domain: {domain}')

    catalog_url = f'https://www.yubico.com/works-with-yubikey/catalog/?protocol=5&sort=popular&search={domain}'
    fido_mentioning = False
    yubikey_urls = []

    driver = setup_driver()
    driver.get(catalog_url)

    time.sleep(3)

    handle_cookie_popup(driver)

    cards = driver.find_elements(By.CLASS_NAME, 'partner-card')
    for card in cards:
        link = card.get_attribute('href')
        yubikey_urls.append(link)

    if len(yubikey_urls) > 0:
        fido_mentioning = True

    return yubikey_urls, fido_mentioning