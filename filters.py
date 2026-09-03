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
