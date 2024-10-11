import time
from random import randint
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from src.modules.user_interaction.cookie_interaction import handle_cookie_popup

login_keywords = ['log in', 'sign in', 'sign on', 'signin', 'login']

def find_login_page(url):
    print(f'[simulate_user_interaction] simulate button-interaction for url: {url}')
    new_links = []
    options = Options()
    options.add_argument('--disable-cookies')  # disable cookies
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(randint(5, 8))  # simulate user delay

        # TODO handle cookie popup
        handle_cookie_popup(driver)
        # TODO handle captchas

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            ec.presence_of_element_located((By.TAG_NAME, 'button')))

        new_links += iterate_element(driver, 'button')
        new_links += iterate_element(driver, 'a')

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