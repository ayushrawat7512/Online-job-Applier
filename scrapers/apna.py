"""
IMPORTANT LIMITATION: Apna.co apni job cards pe exact "posted X hours ago"
text show nahi karta (LinkedIn/Naukri jaisa), isliye is scraper me
MAX_POST_AGE_HOURS wala strict 24h filter apply nahi ho pata - hum sirf
naye/dedup jobs bhejte hai (jo pehle kabhi nahi bheji), jo effectively
"naye jobs" ka kaam kar deta hai jab tak script regularly (30-45 min) chalti
rahe. Ye baaki scrapers se thoda alag/kamzor hai kyunki Apna ka HTML
structure company+title ko ek hi text block me jodta hai, isliye title
aur company clean se separate nahi ho pate - poora text "title" field me
chala jata hai, tum link khol ke details confirm kar lena.

Agar future me ye scraper break ho (Apna apna frontend change kare), sabse
pehle CATEGORY_URLS pe manually visit karke check karo ki HTML structure
kya hai.
"""
import re
import requests
from bs4 import BeautifulSoup

from config import MAX_RESULTS_PER_SOURCE, REQUEST_TIMEOUT, USER_AGENT

CATEGORY_URLS = [
    "https://apna.co/jobs/quality-assurance-jobs",
    "https://apna.co/jobs/qa-jobs",
]

_EXP_PATTERN = re.compile(r"Min\.\s*(\d+)\s*years?", re.IGNORECASE)
_ANY_EXP_PATTERN = re.compile(r"Any experience", re.IGNORECASE)


def fetch_jobs():
    results = []
    headers = {"User-Agent": USER_AGENT}

    for url in CATEGORY_URLS:
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                print(f"[apna] status {resp.status_code} for {url}")
                continue
        except requests.RequestException as e:
            print(f"[apna] request error: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        # Job detail links follow pattern https://apna.co/job/<city>/<slug>-<id>
        links = soup.find_all("a", href=re.compile(r"^https://apna\.co/job/"))

        seen_links = set()
        for a in links[:MAX_RESULTS_PER_SOURCE]:
            link = a["href"].split("?")[0]
            if link in seen_links:
                continue
            seen_links.add(link)

            text = a.get_text(separator=" ", strip=True)
            if not text:
                continue

            results.append(
                {
                    "source": "Apna",
                    "title": text,          # title+company mixed, see note above
                    "company": "See link",
                    "location": "See link",
                    "link": link,
                    "description": text,
                }
            )

    return results
