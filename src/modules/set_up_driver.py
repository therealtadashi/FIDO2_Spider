from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_driver():
    options = Options()
    options.add_argument('--disable-cookies')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(options=options)
    return driver
