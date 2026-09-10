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

# ---------- Company career-site sources ----------
# In teeno platforms ka public JSON API bina login ke accessible hai (company
# ki apni website hi ye data serve karti hai). is_priority se alag concept
# hai - ye sirf "job kaha se aa rahi hai" batata hai.
#
# Har slug wrong/outdated ho sakta hai (companies apna ATS badal sakti hai) -
# aisa hone par us company ka scraper sirf 404 dega aur khud-ba-khud skip ho
# jayega, poori script pe koi asar nahi padega.

# boards-api.greenhouse.io/v1/boards/{slug}/jobs - company slug wahi hota hai
# jo boards.greenhouse.io/<slug> me dikhta hai
GREENHOUSE_COMPANIES = [
    "stripe", "airbnb", "vercel", "shopify", "openai", "anthropic", "notion",
    "linear", "coinbase", "robinhood", "doordash", "instacart", "dropbox",
    "asana", "reddit", "pinterest", "gitlab", "elastic", "hashicorp",
    "confluent", "mongodb", "snowflake", "affirm", "gusto", "squarespace",
    "twilio", "cloudflare", "databricks", "webflow", "postman", "grammarly",
    "miro", "canva", "duolingo", "udemy", "flexport", "benchling", "rippling",
]

# api.lever.co/v0/postings/{slug} - company slug jo jobs.lever.co/<slug> me hai
LEVER_COMPANIES = [
    "figma", "palantir", "spotify", "netflix", "plaid", "brex", "ramp",
    "attentive", "postscript", "eightsleep", "clearcover", "branch",
]

# Workday-hosted companies (tenant/dc/site triple - verify hone tak sirf
# well-known confirmed examples rakhe hai)
WORKDAY_COMPANIES = [
    {"name": "NVIDIA", "tenant": "nvidia", "dc": "wd5", "site": "NVIDIAExternalCareerSite"},
    {"name": "Salesforce", "tenant": "salesforce", "dc": "wd12", "site": "External_Career_Site"},
    {"name": "Adobe", "tenant": "adobe", "dc": "wd5", "site": "external_experienced"},
]
# ---------- Priority region (Delhi NCR) ----------
# Inme se koi bhi jagah job location me mile aur experience requirement
# PRIORITY_MAX_EXPERIENCE_YEARS se kam/equal ho, to us job ko "IMPORTANT"
# tag ke saath alag se highlight karte hai.
PRIORITY_LOCATION_KEYWORDS = [
    "delhi", "ncr", "gurugram", "gurgaon", "haryana",
    "faridabad", "ghaziabad", "noida", "greater noida",
]
PRIORITY_MAX_EXPERIENCE_YEARS = 2

# ---------- Database ----------
DB_PATH = os.environ.get("DB_PATH", "sent_jobs.db")

# ---------- HTTP ----------
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
