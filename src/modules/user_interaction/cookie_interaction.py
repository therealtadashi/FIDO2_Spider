from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By

accept_keywords = ['Accept', 'I Accept', 'Agree', 'OK', 'Accept Cookies', 'I Agree']

def handle_cookie_popup(driver):
    try:
        xpaths = [
            "//*[contains(text(), 'Accept') or contains(text(), 'AGREE')]",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Agree')]",
            "//button[contains(text(), 'OK')]",
            "//a[contains(text(), 'Accept')]",
            "//a[contains(text(), 'Agree')]",
        ]

        for xpath in xpaths:
            try:
                consent_button = driver.find_element(By.XPATH, xpath)
                consent_button.click()
                print("[cookie_interaction] cookie popup accepted.")
                return
            except NoSuchElementException:
                continue
            except ElementClickInterceptedException:
                print("[cookie_interaction] could not click the cookie popup button, element is intercepted.")
                continue

    except Exception as e:
        print(f"[cookie_interaction] Error handling cookie popup: {e}")