from datetime import datetime, timedelta

from src.modules.fido_support.fido2_support import scan_well_known
from src.modules.login_search import LoginPageScraper
from src.modules.webauthn_adoption.dongleauth_webauthn_adoption import dongleauth_fido2_cross_reference
from src.modules.webauthn_adoption.hideez_webauthn_adoption import hideez_fido2_cross_reference
from src.modules.webauthn_adoption.yubikey_webauthn_adoption import yubikey_catalog_fido2_cross_reference
from src.utils.csv_url_reader import read_url
from src.utils.fido2_support_writer import update_fido2_support_json
from src.utils.sso_archive_parser import get_fido_info_for_domain, get_list


yesterday = (datetime.now() - timedelta(days = 7)).strftime('%Y-%m-%d')
datas = get_list(yesterday, '1', '1000')
all_domain_names = [entry['domain'] for entry in datas]

domains = read_url()[11:16]
counter = 0
loginScraper = LoginPageScraper(datas, all_domain_names)

for domain in domains:
    counter += 1
    title = domain.split('.')[0]

    # TODO Cross Reference
    sso_archive = get_fido_info_for_domain(domain, all_domain_names, datas) # sso-archive
    yubikey = yubikey_catalog_fido2_cross_reference(title) # yubikey
    hideez = hideez_fido2_cross_reference(title) # hideez
    dongleauth = dongleauth_fido2_cross_reference(domain, title) # dongleauth

    # TODO Well-Known URI
    well_known = scan_well_known(domain)

    login_urls, support_urls = loginScraper.search_common_login_path_for_url(domain) # Find Login Pages
    update_fido2_support_json(domain, login_urls, support_urls, yubikey, hideez, dongleauth, sso_archive, well_known) # Update FIDO2 Support json file

    if counter == 10:
        break
    print('\n')

# TODO Evaluate FIDO2 Implementation