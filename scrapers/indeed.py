"""
IMPORTANT LIMITATION (as of testing): Indeed uses Cloudflare's managed
bot-protection (Turnstile) which specifically targets datacenter IPs
(like Render's servers) - even sophisticated headless-browser bypasses
fail on datacenter IPs without a paid residential proxy service. This
scraper is kept as best-effort: expect mostly 403s / 0 results from
this source. LinkedIn remains the reliable source.
"""
import requests
from bs4 import BeautifulSoup

from config import MAX_RESULTS_PER_SOURCE, REQUEST_TIMEOUT, USER_AGENT

BASE_URL = "https://in.indeed.com/jobs"
SEARCH_QUERIES = ["QA Engineer", "Software Tester", "Quality Assurance"]


def fetch_jobs():
    results = []
    headers = {"User-Agent": USER_AGENT}

    for query in SEARCH_QUERIES:
        params = {
            "q": query,
            "l": "India",
            "fromage": 1,  # last 24 hours
            "sort": "date",
        }
        try:
            resp = requests.get(
                BASE_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
            )
            if resp.status_code != 200:
                print(f"[indeed] status {resp.status_code} for query '{query}' - likely blocked")
                continue
        except requests.RequestException as e:
            print(f"[indeed] request error: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="job_seen_beacon")

        for card in cards[:MAX_RESULTS_PER_SOURCE]:
            title_el = card.find("h2", class_="jobTitle")
            company_el = card.find("span", {"data-testid": "company-name"})
            location_el = card.find("div", {"data-testid": "text-location"})
            link_el = title_el.find("a") if title_el else None

            if not (title_el and link_el and link_el.get("href")):
                continue

            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location = location_el.get_text(strip=True) if location_el else "India"
            href = link_el["href"]
            link = href if href.startswith("http") else f"https://in.indeed.com{href}"

            results.append(
                {
                    "source": "Indeed",
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "description": title,
                }
            )

    return results
