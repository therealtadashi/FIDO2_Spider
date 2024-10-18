import time
from random import randint
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from src.modules.set_up_driver import setup_driver
from src.modules.user_interaction.cookie_interaction import handle_cookie_popup
from src.modules.user_interaction.translation_keyword import translation_keyword

login_keywords = ['log in', 'sign in', 'sign on', 'signin', 'login']

def find_login_page(url):
    print(f'[simulate_user_interaction] simulate button-interaction for url: {url}')
    new_links = []
    # TODO User-Agent Rotation
    driver = setup_driver()

    try:
        driver.get(url)
        time.sleep(randint(5, 8))  # simulate user delay

        translated_keywords = []

        translate_keywords(driver, translated_keywords) # translate login-keywords
        handle_cookie_popup(driver) # check cookie popup
        # TODO handle captchas

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            ec.presence_of_element_located((By.TAG_NAME, 'button')))

        new_links += iterate_element(driver, 'button')
        new_links += iterate_element(driver, 'a')

        print('[simulate_user_interaction] button interaction finished')

        if translated_keywords in login_keywords:
            login_keywords.remove(translation_keyword)

        return list(set(new_links))

    except Exception as e:
        print(f'[simulate_user_interaction] Error finding sign-in page: {e}')
    finally:
        driver.quit()

    return new_links

# flag has type 'button' or 'a'
def iterate_element(driver, flag):
    elements = driver.find_elements(By.TAG_NAME, flag)
    found_links = []
    try:
        iterate_interact_elements(found_links, driver, elements)
    except Exception as e:
        print(f'[simulate_user_interaction] Error while iterating buttons: {e}')
    return found_links


def visit_page_behind_element(driver, keyword, element):
    try:
        return check_interaction(driver, keyword, element)
    except Exception as  e:
        print(f'[simulate_user_interaction] Error: {e}')
        return False


def iterate_interact_elements(found_links, driver, elements):
    for element in elements:
        for keyword in login_keywords:
            if visit_page_behind_element(driver, keyword, element):
                found_links.append(driver.current_url)
                elements.clear()
                break


def check_interaction(driver, keyword, element):
    if keyword.lower() in element.text.strip().lower():
        element.click()
        time.sleep(randint(3, 6))
        current_url = driver.current_url
        print(f'[simulate_user_interaction] new link found: {current_url}')
        return True
    return False


def translate_keywords(driver, translated_keywords):
    lang = driver.find_element(By.XPATH, '//html').get_attribute('lang')
    if '-' in lang:
        lang = lang.split('-')[0]  # filter regional language
    if lang != 'en':
        translated_keywords.extend(translation_keyword[lang])
        login_keywords.extend(translated_keywords)