from src.modules.login_search import search_common_login_path_for_url
from src.utils.csv_url_reader import read_url
from src.utils.fido2_support_writer import update_fido2_support_json

domains = read_url()
counter = 0
for domain in domains:
    counter += 1
    login_urls, support_urls = search_common_login_path_for_url(domain)
    update_fido2_support_json(domain, login_urls, support_urls)
    if counter == 3:
        break
    print('\n')