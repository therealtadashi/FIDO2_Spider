import time
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from src.modules.set_up_driver import setup_driver
from src.modules.user_interaction.cookie_interaction import handle_cookie_popup


def hideez_fido2_cross_reference(title):
    print(f'[hideez_webauthn_adoption] searching for FIDO2 on hideez for the domain: {title}')

    catalog_url = 'https://hideez.com/en-de/pages/supported-services'
    results = {}
    fido_support = False

    driver = setup_driver()
    driver.get(catalog_url)
    time.sleep(3)

    handle_cookie_popup(driver)

    # select FIDO2/WebAuthn from selector
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, 'protocols')))
    select_element = Select(driver.find_element(By.ID, 'protocols'))
    select_element.select_by_value('FIDO2/WebAuthn') # select FIDO2/WebAuthn

    # search for input element
    search_input = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.NAME, 'search')))
    search_input.send_keys(title)
    search_input.send_keys(Keys.RETURN)

    try:
        # extract info from blocks
        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'section-inner.filter-results')))
        section_inner = driver.find_element(By.CLASS_NAME, 'section-inner.filter-results')
        blocks = section_inner.find_elements(By.CLASS_NAME, 'ServiceBlock')
        for block in blocks:
            result = {
                'description': '',
                'link': ''
            }
            name = block.find_element(By.CLASS_NAME, 'ServiceBlock--heading').text.strip()
            result['description'] = block.find_element(By.CLASS_NAME, 'ServiceBlock--content').text.strip()
            try:
                result['link'] = block.find_element(By.CLASS_NAME, 'ServiceBlock--link').get_attribute('href')
            except NoSuchElementException:
                pass
            results[name] = result
    except TimeoutException:
        pass

    if results:
        fido_support = True

    hideez = {
        'hideez_block': results,
        'fido_support': fido_support
    }

    driver.quit()

    return hideez