"""
LinkedIn ka "guest" job search endpoint use karta hai jo login ke bina bhi
public search results deta hai (wahi jo linkedin.com/jobs pe dikhta hai
"Sign in to see more" wale page ke peeche). Ye login-based automation
nahi hai, sirf public listing HTML fetch kar rahe hai - isliye account-ban
ka risk nahi hai (koi account use hi nahi ho raha).

Note: LinkedIn apna HTML structure/class names kabhi kabhi badalta hai,
isliye agar ye scraper achanak 0 results dena start kare to selectors
check/update karne padenge.
"""
import requests
from bs4 import BeautifulSoup

from config import SEARCH_LOCATION, MAX_RESULTS_PER_SOURCE, REQUEST_TIMEOUT, USER_AGENT

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# f_TPR=r86400 -> pichle 24 ghante ke posts
SEARCH_QUERIES = ["QA Engineer", "Software Tester", "Quality Assurance"]


def fetch_jobs():
    results = []
    headers = {"User-Agent": USER_AGENT}

    for query in SEARCH_QUERIES:
        params = {
            "keywords": query,
            "location": SEARCH_LOCATION,
            "f_TPR": "r86400",  # last 24 hours
            "position": 1,
            "pageNum": 0,
        }
        try:
            resp = requests.get(
                BASE_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
            )
            if resp.status_code != 200:
                print(f"[linkedin] status {resp.status_code} for query '{query}'")
                continue
        except requests.RequestException as e:
            print(f"[linkedin] request error: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("li")

        for card in cards[:MAX_RESULTS_PER_SOURCE]:
            title_el = card.find("h3", class_="base-search-card__title")
            company_el = card.find("h4", class_="base-search-card__subtitle")
            location_el = card.find("span", class_="job-search-card__location")
            link_el = card.find("a", class_="base-card__full-link")

            if not (title_el and link_el):
                continue

            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location = location_el.get_text(strip=True) if location_el else SEARCH_LOCATION
            link = link_el["href"].split("?")[0]

            results.append(
                {
                    "source": "LinkedIn",
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "description": title,  # guest endpoint description nahi deta
                }
            )

    return results
