"""
Naukri.com apna internal search API (jo unki website khud use karti hai)
call karta hai. Ye bhi login ke bina public data hai. Naukri ko kuch
specific headers chahiye (appid/systemid) warna 403 deta hai - ye headers
publicly known hai aur Naukri ki website khud bhi yahi bhejti hai.

Agar future me Naukri apna API change kare aur ye scraper fail ho, sabse
pehle headers/endpoint check karna.
"""
import requests
from datetime import datetime, timedelta, timezone

from config import MAX_RESULTS_PER_SOURCE, REQUEST_TIMEOUT, USER_AGENT

BASE_URL = "https://www.naukri.com/jobapi/v3/search"

SEARCH_QUERIES = ["QA Engineer", "Software Tester", "Quality Assurance"]


def fetch_jobs():
    results = []
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "appid": "109",
        "systemid": "Naukri",
        "Referer": "https://www.naukri.com/",
    }

    for query in SEARCH_QUERIES:
        params = {
            "noOfResults": MAX_RESULTS_PER_SOURCE,
            "urlType": "search_by_keyword",
            "searchType": "adv",
            "keyword": query,
            "location": "india",
            "days": 1,  # last 24 hours
            "sort": "f",
        }
        try:
            resp = requests.get(
                BASE_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
            )
            if resp.status_code != 200:
                print(f"[naukri] status {resp.status_code} for query '{query}'")
                continue
            data = resp.json()
        except (requests.RequestException, ValueError) as e:
            print(f"[naukri] request/parse error: {e}")
            continue

        for job in data.get("jobDetails", []):
            title = job.get("title", "")
            company = job.get("companyName", "Unknown")
            location = job.get("placeholders", [{}])[0].get("label", "India") \
                if job.get("placeholders") else "India"
            job_id = job.get("jobId")
            link = f"https://www.naukri.com/job-listings-{job_id}" if job_id else job.get("jdURL", "")
            description = job.get("jobDescription", "") or title

            if not link:
                continue

            results.append(
                {
                    "source": "Naukri",
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "description": description,
                }
            )

    return results
