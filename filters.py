"""
Do filters:
1. is_qa_job()      -> title/description QA/testing role se match karta hai ya nahi
2. extract_experience() -> job text se minimum required experience (years) nikalta hai
3. passes_experience_filter() -> MAX_EXPERIENCE_YEARS se kam/equal hai ya experience
                                  mention hi nahi hai (is case me include karte hai,
                                  taaki koi relevant job miss na ho - tum khud review kar lena)
"""
import re
from config import QA_KEYWORDS, MAX_EXPERIENCE_YEARS

# Patterns jaise: "2-5 years", "0-2 yrs", "3+ years", "fresher", "1 to 3 years"
_RANGE_PATTERN = re.compile(
    r"(\d+)\s*(?:-|to)\s*(\d+)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE
)
_PLUS_PATTERN = re.compile(r"(\d+)\s*\+\s*(?:years?|yrs?)", re.IGNORECASE)
_SINGLE_PATTERN = re.compile(r"(\d+)\s*(?:years?|yrs?)", re.IGNORECASE)
_FRESHER_PATTERN = re.compile(r"\bfresher(s)?\b", re.IGNORECASE)


_QA_WORD_PATTERN = re.compile(r"\bqa\b", re.IGNORECASE)


def is_qa_job(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()
    if any(keyword in text for keyword in QA_KEYWORDS):
        return True
    # Standalone "QA" word bhi match karo (e.g. "QA Manager", "QA Lead")
    # word-boundary use kiya hai taaki "qa" kisi aur word ke andar (jaise
    # "aqa" ya "sqa" jaisi cheez) galti se match na kare.
    return bool(_QA_WORD_PATTERN.search(text))


def extract_experience(text: str):
    """Returns (min_years, max_years) ya None agar kuch nahi mila."""
    if not text:
        return None

    if _FRESHER_PATTERN.search(text):
        return (0, 0)

    match = _RANGE_PATTERN.search(text)
    if match:
        return (int(match.group(1)), int(match.group(2)))

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
