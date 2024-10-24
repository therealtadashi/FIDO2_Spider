from datetime import datetime, timedelta
from src.modules.fido_support.fido2_support import scan_well_known
from src.modules.login_search import LoginPageScraper
from src.modules.cross_reference_adoption.dongleauth_webauthn_adoption import dongleauth_fido2_cross_reference
from src.modules.cross_reference_adoption.hideez_webauthn_adoption import hideez_fido2_cross_reference
from src.modules.cross_reference_adoption.yubikey_webauthn_adoption import yubikey_catalog_fido2_cross_reference
from src.utils.csv_url_reader import read_url
from src.utils.fido2_support_writer import update_login_search, update_well_known, update_cross_reference
from src.utils.sso_archive_parser import get_fido_info_for_domain, get_list


yesterday = (datetime.now() - timedelta(days = 7)).strftime('%Y-%m-%d')
datas = get_list(yesterday, '1', '1000')
all_domain_names = [entry['domain'] for entry in datas]

domains = read_url()[0:5]
loginScraper = LoginPageScraper(datas, all_domain_names)

for domain in domains:
    title = domain.split('.')[0]

    # TODO Cross Reference
    sso_archive = get_fido_info_for_domain(domain, all_domain_names, datas) # sso-archive
    yubikey = yubikey_catalog_fido2_cross_reference(title) # yubikey
    hideez = hideez_fido2_cross_reference(title) # hideez
    dongleauth = dongleauth_fido2_cross_reference(domain, title) # dongleauth
    update_cross_reference(domain, sso_archive, yubikey, hideez, dongleauth)

    # TODO Well-Known URI
    well_known = scan_well_known(domain)
    update_well_known(domain, well_known)

    # TODO Search for Login Pages
    login_search = loginScraper.search_common_login_path_for_url(domain) # Find Login Pages
    update_login_search(domain, login_search)

    print('\n')

# TODO Evaluate FIDO2 Implementation