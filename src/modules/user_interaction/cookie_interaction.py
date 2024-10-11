import time

from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

cookie_keywords = ['allow', 'agree', 'accept', 'decline', 'reject']


def handle_cookie_popup(driver):
    print('[cookie_interaction] searching for cookie popup')
    time.sleep(2)
    for tag in ['button', 'a', 'span']:
        iterate_elements(driver, tag)
    time.sleep(2)


def iterate_elements(driver, tag):
    elements = driver.find_elements(By.TAG_NAME, tag)
    for element in elements:
        for keyword in cookie_keywords:
            if not keyword.lower() in element.text.strip().lower():
                continue
            try:
                WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable(element)
                )
                ActionChains(driver).move_to_element(element).click().perform()
                return True
            except StaleElementReferenceException:
                return False
    elements.clear()