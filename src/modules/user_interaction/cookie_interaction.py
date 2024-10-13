import time
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

cookie_keywords = ['allow', 'agree', 'accept', 'decline', 'reject', 'Allow', 'Agree', 'Decline', 'Reject', 'Accept']


def handle_cookie_popup(driver):
    print('[cookie_interaction] searching for cookie popup')
    tags = ['button', 'span', 'a']
    time.sleep(2)
    for tag in tags:
        if not check_elements(driver, tag):
            continue
        if iterate_elements(driver, tag):
            break
    time.sleep(2)
    print('[cookie_interaction] cookie interaction finished')


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
                time.sleep(1)
                if not element.is_displayed():
                    return True
            except StaleElementReferenceException:
                elements.clear()
                return True
    elements.clear()
    return False


def check_elements(driver, tag):
    for keyword in cookie_keywords:
        try:
            driver.find_element(By.XPATH, f"//{tag}[contains(text(), '{keyword}')]")
            return True
        except NoSuchElementException:
            continue
    return False