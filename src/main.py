from datetime import datetime, timedelta
from src.modules.login_search import LoginPageScraper
from src.modules.webauthn_adoption.yubikey_webauthn_adoption import yubikey_catalog_fido2_cross_reference
from src.utils.csv_url_reader import read_url
from src.utils.fido2_support_writer import update_fido2_support_json
from src.utils.sso_archive_parser import get_fido_info_for_domain, get_list

yesterday = (datetime.now() - timedelta(days = 7)).strftime('%Y-%m-%d')
datas = get_list(yesterday, '1', '1000')
all_domain_names = [entry['domain'] for entry in datas]

domains = read_url()
counter = 0
loginScraper = LoginPageScraper()

for domain in domains:
    counter += 1
    title = domain.split('.')[0]

    # TODO Find WebAuthn Adoption for "domain" on Adoption Lists

    sso_archive = get_fido_info_for_domain(domain, all_domain_names, datas) # sso-archive
    yubikey = yubikey_catalog_fido2_cross_reference(title) # yubikey

    login_urls, support_urls = loginScraper.search_common_login_path_for_url(domain) # Find Login Pages
    update_fido2_support_json(domain, login_urls, support_urls, yubikey, sso_archive) # Update FIDO2 Support json file

    if counter == 3:
        break
    print('\n')

# TODO Evaluate FIDO2 Implementation