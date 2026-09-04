"""
Do filters:
1. is_qa_job()      -> title/description QA/testing role se match karta hai ya nahi
2. extract_experience() -> job text se minimum required experience (years) nikalta hai
3. passes_experience_filter() -> MAX_EXPERIENCE_YEARS se kam/equal hai ya experience
                                  mention hi nahi hai (is case me include karte hai,
                                  taaki koi relevant job miss na ho - tum khud review kar lena)
"""
import re
from config import QA_KEYWORDS, MAX_EXPERIENCE_YEARS, PRIORITY_LOCATION_KEYWORDS, PRIORITY_MAX_EXPERIENCE_YEARS

# Patterns jaise: "2-5 years", "0-2 yrs", "3+ years", "fresher", "1 to 3 years",
# "minimum 2 years", "at least 3 yrs", "min. 4 years"
_RANGE_PATTERN = re.compile(
    r"(\d+)\s*(?:-|to)\s*(\d+)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE
)
_MIN_PATTERN = re.compile(
    r"(?:minimum|min\.?|at\s*least|over)\s*(\d+)\s*(?:years?|yrs?)", re.IGNORECASE
)
_PLUS_PATTERN = re.compile(r"(\d+)\s*\+\s*(?:years?|yrs?)", re.IGNORECASE)
_SINGLE_PATTERN = re.compile(r"(\d+)\s*(?:years?|yrs?)", re.IGNORECASE)
_FRESHER_PATTERN = re.compile(r"\bfresher(s)?\b", re.IGNORECASE)


_QA_WORD_PATTERN = re.compile(r"\bqa\b", re.IGNORECASE)

# Non-software domains jaha "Quality Analyst/QA" title kaam karti hai lekin
# software testing se koi lena dena nahi hota (BPO, manufacturing,
# call-center, hospitality, etc.) - inhe exclude karte hai.
_NON_SOFTWARE_DOMAIN_KEYWORDS = [
    "bpo", "call center", "call centre", "voice process", "non-voice",
    "manufacturing", "production line", "shop floor", "garment", "textile",
    "food safety", "food quality", "pharma quality", "warehouse",
    "housekeeping", "hospitality", "hotel", "restaurant", "kitchen",
    "customer support quality", "customer service quality",
    "quality control inspector", "quality inspector", "welding",
    "supply chain quality", "logistics quality", "civil quality",
    "construction quality", "site quality", "field quality",
]

# In indicators mein se koi bhi mile to samajh lo ye genuinely software/tech
# testing role hai, chahe non-software domain keyword bhi text me kahin ho
# (jaise agar "pharma" company software QA hire kar rahi ho to bhi allow ho)
_SOFTWARE_CONTEXT_KEYWORDS = [
    "software", "application", "web app", "mobile app", "api testing",
    "automation testing", "test automation", "selenium", "playwright",
    "cypress", "appium", "sdet", "test case", "test script", "regression testing",
    "bug tracking", "postman", "sql", "test plan", "qa engineer",
    "quality assurance engineer", "software tester", "software testing",
    "manual testing", "test engineer",
]


def is_qa_job(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()

    matched_qa = any(keyword in text for keyword in QA_KEYWORDS) or bool(
        _QA_WORD_PATTERN.search(text)
    )
    if not matched_qa:
        return False

    # Agar non-software domain ka signal hai, tabhi reject karo jab
    # software/tech context ka koi indicator bhi na mile.
    has_non_software_signal = any(kw in text for kw in _NON_SOFTWARE_DOMAIN_KEYWORDS)
    has_software_signal = any(kw in text for kw in _SOFTWARE_CONTEXT_KEYWORDS)

    if has_non_software_signal and not has_software_signal:
        return False

    return True


def extract_experience(text: str):
    """Returns (min_years, max_years) ya None agar kuch nahi mila."""
    if not text:
        return None

    if _FRESHER_PATTERN.search(text):
        return (0, 0)

    match = _RANGE_PATTERN.search(text)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    match = _MIN_PATTERN.search(text)
    if match:
        low = int(match.group(1))
        return (low, low + 3)  # rough upper estimate

    match = _PLUS_PATTERN.search(text)
    if match:
        low = int(match.group(1))
        return (low, low + 3)  # rough upper estimate

    match = _SINGLE_PATTERN.search(text)
    if match:
        val = int(match.group(1))
        return (val, val)

    return None


def passes_experience_filter(text: str) -> bool:
    exp = extract_experience(text)
    if exp is None:
        # Experience mention nahi mila - safer side pe include karo,
        # tum link kholke khud dekh lena.
        return True
    min_years, _ = exp
    return min_years <= MAX_EXPERIENCE_YEARS


def is_priority_job(location: str, exp_tuple) -> bool:
    """
    Delhi NCR region (Delhi, Gurugram, Haryana, Faridabad, Ghaziabad, Noida,
    Greater Noida) ki job hai aur experience requirement 2 years tak hai,
    to True - is job ko "IMPORTANT" tag ke saath highlight karna hai.
    Experience explicitly pata na ho to priority nahi maante (safe default).
    """
    if not location or exp_tuple is None:
        return False
    location_lower = location.lower()
    is_ncr = any(kw in location_lower for kw in PRIORITY_LOCATION_KEYWORDS)
    if not is_ncr:
        return False
    min_years, _ = exp_tuple
    return min_years <= PRIORITY_MAX_EXPERIENCE_YEARS


# ---------- Salary / package extraction ----------
# Common Indian formats: "₹5-8 LPA", "12 LPA", "₹40,000 - 50,000/month",
# "5,00,000 - 8,00,000 per annum", "$60k - $80k"
_LPA_RANGE_PATTERN = re.compile(
    r"₹?\s*(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*LPA", re.IGNORECASE
)
_LPA_SINGLE_PATTERN = re.compile(r"₹?\s*(\d+(?:\.\d+)?)\s*LPA", re.IGNORECASE)
_RUPEE_MONTH_PATTERN = re.compile(
    r"₹\s*([\d,]+)\s*(?:-|to)\s*₹?\s*([\d,]+)\s*(?:per\s*month|/\s*month|a\s*month)",
    re.IGNORECASE,
)
_RUPEE_ANNUM_PATTERN = re.compile(
    r"₹\s*([\d,]+)\s*(?:-|to)\s*₹?\s*([\d,]+)\s*(?:per\s*annum|/\s*annum|p\.?a\.?)",
    re.IGNORECASE,
)
_USD_K_RANGE_PATTERN = re.compile(
    r"\$\s*(\d+)\s*[kK]\s*(?:-|to)\s*\$?\s*(\d+)\s*[kK]"
)


def extract_salary(text: str):
    """Returns a human-readable salary/package string, or None if not found."""
    if not text:
        return None

    m = _LPA_RANGE_PATTERN.search(text)
    if m:
        return f"₹{m.group(1)}-{m.group(2)} LPA"

    m = _LPA_SINGLE_PATTERN.search(text)
    if m:
        return f"₹{m.group(1)} LPA"

    m = _RUPEE_MONTH_PATTERN.search(text)
    if m:
        return f"₹{m.group(1)}-{m.group(2)} / month"

    m = _RUPEE_ANNUM_PATTERN.search(text)
    if m:
        return f"₹{m.group(1)}-{m.group(2)} / annum"

    m = _USD_K_RANGE_PATTERN.search(text)
    if m:
        return f"${m.group(1)}k-${m.group(2)}k"

    return None
