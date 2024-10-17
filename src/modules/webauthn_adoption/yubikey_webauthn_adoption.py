import time
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from src.modules.set_up_driver import setup_driver
from src.modules.user_interaction.cookie_interaction import handle_cookie_popup


def yubikey_catalog_fido2_cross_reference(title):
    print(f'[yubikey_webauthn_adoption] searching for FIDO2 on yubikey catalog for the domain: {title}')

    catalog_url = f'https://www.yubico.com/works-with-yubikey/catalog/?protocol=5&sort=popular&search={title}'
    yubikey_urls = []
    fido_support = False

    driver = setup_driver()
    driver.get(catalog_url)
    time.sleep(3)

    handle_cookie_popup(driver)

    try:
        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'partner-card')))
        cards = driver.find_elements(By.CLASS_NAME, 'partner-card')
        for card in cards:
            link = card.get_attribute('href')
            yubikey_urls.append(link)
    except TimeoutException:
        pass

    if len(yubikey_urls) > 0:
        fido_support = True

    yubikey = {
        'yubikey_url': yubikey_urls,
        'fido_support': fido_support
    }

    driver.quit()

    return yubikey