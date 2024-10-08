# FIDO2 WebScraper

This webscraper searches for login pages from the Urls listed in the tranco list.
After finding the login pages the scraper looks whether the webpage supports FIDO2 frameworks or not.

---

# Problem with Dynamic Scraping

Common problems surrounding dynamic scraping:

- **Client Side Rendering** (need for manual interaction)
- **Crawl-Duration**
- **Large Website Size**: use **ETL** tools -> json, csv format -> store on Apache hadoop, Apache Spark
- **IP-bans**
- **Region Specific Websites**
- **Respecting Website Rules** (robots.txt)

---

# Dynamic Web Scraping Process to find WebAuthn Login

search the login pages from the url listed in **tranco**:

1. create common sub-URL pattern list to access login pages
   - for example: /login, /user, /auth, /signin, /account
2. get tranco list
3. access tranco csv
4. make csv iterable
   - **Parallelise CSV Access**: If working with very large CSVs, split the work across multiple threads to improve performance when scraping
5. iterate through the list
   - filter domains not accessible by TLS - secure connection
6. access robots.txt to respect sites rules
7. filter all disallowed url patterns from common sub-URL pattern list
8. scrape with the rest of the allowed patterns
9. Dynamic Discovery: Parse homepage HTML for links or redirects leading to a login page
10. search for WebAuthn
    - **API Interaction**: Instead of just searching for WebAuthn features passively, consider interacting with the site’s authentication mechanism by simulating a WebAuthn request to verify its presence.
    - **Improve Accuracy**: Look for additional WebAuthn indicators, like the presence of WebAuthn-specific polyfills or reliance on specific authentication services that support WebAuthn (e.g., Okta, Auth0).

---
