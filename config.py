"""
Central configuration. Sab secrets Render Environment Variables se aayenge -
kabhi bhi yaha hardcode mat karna, warna GitHub pe leak ho jayega.
"""
import os

# ---------- Telegram ----------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ---------- Search settings ----------
# QA / Testing role ke liye keywords - inme se koi bhi title/description me
# mile to job "relevant" maana jayega.
QA_KEYWORDS = [
    "qa engineer", "quality assurance", "software tester", "test engineer",
    "sdet", "automation tester", "manual tester", "software testing",
    "qa analyst", "test analyst", "quality analyst",
]

# Experience cutoff - isse zyada minimum experience wali job skip ho jayegi
MAX_EXPERIENCE_YEARS = 5

# Kitne purane job posts allow karne hai (ghanto me)
MAX_POST_AGE_HOURS = 24

# Har run me kitni jobs max fetch karni hai per source (rate-limit friendly)
MAX_RESULTS_PER_SOURCE = 25

# Location - pan India, remote + onsite. Search query me location blank/wide
# rakhenge, "India" keyword use karenge jaha zaroori ho.
SEARCH_LOCATION = "India"

# ---------- Database ----------
DB_PATH = os.environ.get("DB_PATH", "sent_jobs.db")

# ---------- HTTP ----------
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
