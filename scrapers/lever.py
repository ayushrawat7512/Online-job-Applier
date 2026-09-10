"""
Lever (api.lever.co) bhi ek public JSON API hai, Greenhouse jaisa hi -
company ki apni careers page (jobs.lever.co/<slug>) yehi API call karti
hai. LEVER_COMPANIES list (config.py) se saari companies check hoti hai.

Endpoint: https://api.lever.co/v0/postings/{slug}?mode=json
Response me descriptionPlain already included hota hai - alag se JD fetch
ki zaroorat nahi.
"""
import requests

from config import LEVER_COMPANIES, REQUEST_TIMEOUT, USER_AGENT

BASE_URL = "https://api.lever.co/v0/postings/{slug}"


def fetch_jobs():
    results = []
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    for slug in LEVER_COMPANIES:
        url = BASE_URL.format(slug=slug)
        try:
            resp = requests.get(
                url, params={"mode": "json"}, headers=headers, timeout=REQUEST_TIMEOUT
            )
            if resp.status_code != 200:
                continue
            jobs = resp.json()
            if not isinstance(jobs, list):
                continue
        except (requests.RequestException, ValueError):
            continue

        for job in jobs:
            title = job.get("text", "")
            categories = job.get("categories", {}) or {}
            location = categories.get("location", "") or ""
            link = job.get("hostedUrl", "")
            description = job.get("descriptionPlain") or job.get("description") or title

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
