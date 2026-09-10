"""
Workday-hosted career sites (*.myworkdayjobs.com) bhi ek public JSON API
serve karte hai - bina login. WORKDAY_COMPANIES list (config.py) me
{tenant, dc, site} triples hai.

Endpoint: POST https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
Body: {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "QA"}

NOTE: List response me full job description nahi hoti (sirf title,
location, posted date) - isliye is source ke jobs me Experience/Package
zyada tar N/A aayega, jab tak job title mein hi kuch info na ho. Ye
consistent hai baaki jagah jaisa "jo info nahi mili wahan N/A" rule ke
saath.
"""
import requests

from config import WORKDAY_COMPANIES, REQUEST_TIMEOUT, USER_AGENT

SEARCH_TERMS = ["QA", "Quality Assurance", "Software Tester", "Test Engineer"]


def fetch_jobs():
    results = []
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    for company in WORKDAY_COMPANIES:
        tenant = company["tenant"]
        dc = company["dc"]
        site = company["site"]
        name = company["name"]
        base_url = f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        board_url = f"https://{tenant}.{dc}.myworkdayjobs.com/{site}"

        seen_paths = set()
        for term in SEARCH_TERMS:
            body = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": term}
            try:
                resp = requests.post(
                    base_url, json=body, headers=headers, timeout=REQUEST_TIMEOUT
                )
                if resp.status_code != 200:
                    continue
                data = resp.json()
            except (requests.RequestException, ValueError):
                continue

            for posting in data.get("jobPostings", []):
                title = posting.get("title", "")
                location = posting.get("locationsText", "") or ""
                external_path = posting.get("externalPath", "")

                if not external_path or external_path in seen_paths:
                    continue
                seen_paths.add(external_path)

                if "india" not in location.lower() and "remote" not in location.lower():
                    continue

                link = board_url + external_path

                results.append(
                    {
                        "source": f"{name} (Careers Website)",
                        "title": title,
                        "company": name,
                        "location": location or "India",
                        "link": link,
                        "description": title,  # list API me full JD nahi hoti
                    }
                )

    return results
