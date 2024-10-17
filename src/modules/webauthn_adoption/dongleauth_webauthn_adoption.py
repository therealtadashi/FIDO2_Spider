from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from src.modules.set_up_driver import setup_driver


def dongleauth_fido2_cross_reference(domain, title):
    print(f'[dongleauth_webauthn_adoption] searching for FIDO2 on dongleauth for the domain: {title}')

    catalog_url = 'https://www.dongleauth.com/'
    results = {}

    driver = setup_driver()
    driver.get(catalog_url)

    search_input = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, 'jets-search')))
    search_input.send_keys(domain)
    search_input.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(lambda d: d.page_source)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all(class_='desktop-tr')
    jets_elements = [
        row for row in rows if row.get('data-jets') and title.lower() in row['data-jets'].lower()
    ]

    for element in jets_elements:
        result = {}
        try:
            link = element.find(class_='name', href=True)
            if link:
                result['link'] = link['href']
                name = link.text.strip()
                docs = element.find(class_='positive icon').find('a', href=True)
                result['docs'] = docs['href'] if docs else None
                result['u2f'] = element.find('i', title='Universal 2nd Factor (U2F)') is not None
                results[name] = result
        except AttributeError:
            pass

    driver.quit()

    dongleauth = {
        'results': results,
    }

    return dongleauth
