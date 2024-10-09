import time
from random import randint
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

login_keywords = ['log in', 'sign in', 'sign on', 'signin', 'login']
new_links = []

def find_login_page(url):
    print(f'[simulate_user_interaction] simulate button-interaction for url: {url}')

    try:
        options = Options()
        options.add_argument('--disable-cookies') # disable cookies
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        driver = webdriver.Chrome(options = options)

        driver.get(url)
        time.sleep(randint(3, 6))

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            ec.presence_of_element_located((By.TAG_NAME, 'button')))

        iterate_element(driver, 'button')
        iterate_element(driver, 'a')

        driver.quit()

        return new_links

    except Exception as e:
        print(f'[simulate_user_interaction] Error finding sign-in page: {e}')

# flag has type 'button' or 'a'
def iterate_element(driver, flag):
    elements = driver.find_elements(By.TAG_NAME, flag)
    try:
        iterate_interact_elements(driver, elements)

    except Exception as e:
        print(f'[simulate_user_interaction] Error while iterating buttons: {e}')


def visit_page_behind_element(driver, keyword, element):
    try:
        return check_interaction(driver, keyword, element)
    except Exception as  e:
        print(f'[simulate_user_interaction] Error: {e}')
        return False


def iterate_interact_elements(driver, elements):
    for element in elements:
        for keyword in login_keywords:
            if visit_page_behind_element(driver, keyword, element):
                elements.clear()
                break


def check_interaction(driver, keyword, button):
    if keyword.lower() not in button.text.strip().lower():
        return False
    button.click()
    time.sleep(randint(3, 6))
    current_url = driver.current_url
    if current_url not in new_links:
        print(f'[simulate_user_interaction] new link found: {current_url}')
        new_links.append(current_url)
        return True
    return False