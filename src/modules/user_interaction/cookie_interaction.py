import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def handle_cookie_popup(driver):
    print('[cookie_interaction] searching for cookies')
    try:
        xpaths = [
            "//span[contains(text(), 'Allow all cookies') or contains(text(), 'Accept') or contains(text(), 'agree') or contains(text(), 'OK') or contains(text(), 'Allow')]",
            "//*[contains(text(), 'Accept') or contains(text(), 'AGREE') or contains(text(), 'accept') or contains(text(), 'Allow')]",
            "//button[contains(text(), 'Accept') or contains(text(), 'agree') or contains(text(), 'OK') or contains(text(), 'Allow')]",
            "//a[contains(text(), 'Accept') or contains(text(), 'agree') or contains(text(), 'OK') or contains(text(), 'Allow')]"
        ]
        for xpath in xpaths:
            try:
                consent_button = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.XPATH, xpath))
                )
                ActionChains(driver).move_to_element(consent_button).click().perform()
                print('[cookie_interaction] cookie popup accepted.')
                return
            except Exception as e:
                print(f'[cookie_interaction] Error while interacting with cookie popup {e}')
                continue
    except Exception as e:
        print(f'[cookie_interaction] Error handling cookie popup: {e}')
    finally:
        print('[cookie_interaction] interaction finished')
        time.sleep(2)