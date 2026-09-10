"""
Greenhouse (boards-api.greenhouse.io) ek public JSON API hai jo bina login
ke accessible hai - companies apni khud ki website pe yehi API call karti
hai. GREENHOUSE_COMPANIES list (config.py) me jitni bhi companies hai,
unki saari open jobs yaha se fetch hoti hai, phir QA-relevance filter
baaki scrapers jaisa hi lagta hai (main.py me).

Endpoint: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
content=true se poora job description (HTML) bhi mil jata hai - isliye is
source ke liye alag se JD-fetch (jaisa LinkedIn ke liye karte hai) ki
zaroorat nahi padti, sab ek hi call me mil jata hai.
"""
import requests
from bs4 import BeautifulSoup

from config import GREENHOUSE_COMPANIES, REQUEST_TIMEOUT, USER_AGENT

BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def fetch_jobs():
    results = []
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    for slug in GREENHOUSE_COMPANIES:
        url = BASE_URL.format(slug=slug)
        try:
            resp = requests.get(
                url, params={"content": "true"}, headers=headers, timeout=REQUEST_TIMEOUT
            )
            if resp.status_code != 200:
                # Galat/outdated slug - chup-chaap skip karo, crash nahi hona
                # chahiye
                continue
            data = resp.json()
        except (requests.RequestException, ValueError):
            continue

        for job in data.get("jobs", []):
            title = job.get("title", "")
            location = (job.get("location") or {}).get("name", "")
            link = job.get("absolute_url", "")
            content_html = job.get("content", "")
            description = BeautifulSoup(content_html, "html.parser").get_text(
                separator=" ", strip=True
            ) if content_html else title

            # Sirf India-based jobs chahiye (pan-India, remote+onsite)
            if "india" not in location.lower() and "remote" not in location.lower():
                continue

            if not link:
                continue

            results.append(
                {
                    "source": f"{slug.capitalize()} (Careers Website)",
                    "title": title,
                    "company": slug.capitalize(),
                    "location": location or "India",
                    "link": link,
                    "description": description,
                }
            )

    return results
