"""
Entry point. Render pe ye script Cron Job / Background Worker ke andar
periodically (har 30-45 min) chalegi. Har run me:
  1. LinkedIn, Naukri, Indeed, Apna se jobs fetch karega
  2. QA-relevance + experience (<=5 years) filter apply karega
  3. Jo job pehle kabhi nahi bheji, usko Telegram pe bhejega
  4. DB me mark kar dega taaki dobara na bheje
"""
import sys
import time

from db import init_db, already_sent, mark_sent
from filters import is_qa_job, passes_experience_filter, extract_experience, extract_salary, is_priority_job
from notifier import send_job_alert, send_text
from scrapers import linkedin, naukri, indeed, apna, greenhouse, lever, workday

SCRAPERS = [
    ("LinkedIn", linkedin.fetch_jobs),
    ("Greenhouse", greenhouse.fetch_jobs),
    ("Lever", lever.fetch_jobs),
    ("Workday", workday.fetch_jobs),
    # Naukri, Indeed, Apna disabled - modern anti-bot/JS-rendering protection
    # blocks them without a paid proxy service. See README for details.
    # Uncomment below to re-enable if you set up a paid scraping service:
    # ("Naukri", naukri.fetch_jobs),
    # ("Indeed", indeed.fetch_jobs),
    # ("Apna", apna.fetch_jobs),
]


def format_experience(text):
    exp = extract_experience(text)
    if exp is None:
        return "N/A"
    low, high = exp
    if low == 0 and high == 0:
        return "Fresher"
    if low == high:
        return f"{low} yrs"
    return f"{low}-{high} yrs"


def run_once():
    init_db()
    total_new = 0

    for name, fetch_fn in SCRAPERS:
        print(f"--- Checking {name} ---")
        try:
            jobs = fetch_fn()
        except Exception as e:
            # Ek scraper fail ho to baaki chalte rahe - poori script crash na ho
            print(f"[main] {name} scraper failed entirely: {e}")
            continue

        print(f"[main] {name}: {len(jobs)} raw results")
        new_count = 0

        for job in jobs:
            link = job.get("link")
            title = job.get("title", "")
            description = job.get("description", "") or title

            if not link:
                continue
            if already_sent(link):
                continue
            if not is_qa_job(title, description):
                continue
            if not passes_experience_filter(f"{title} {description}"):
                continue

            # Job bhejne layak hai - ab uska poora JD fetch karke real
            # Experience aur Package nikalne ki koshish karo (sirf LinkedIn
            # ke paas ye capability hai abhi; fail ho to title-level info
            # pe hi fallback ho jata hai, alert phir bhi jayega)
            full_text = description
            if job["source"] == "LinkedIn":
                try:
                    jd = linkedin.fetch_job_description(link)
                    if jd:
                        full_text = jd
                except Exception as e:
                    print(f"[main] JD fetch failed for {link}: {e}")

            send_job_alert(
                source=job["source"],
                title=title,
                company=job.get("company", "Unknown"),
                location=job.get("location", ""),
                experience_text=format_experience(full_text),
                salary_text=extract_salary(full_text),
                link=link,
                is_priority=is_priority_job(job.get("location", ""), extract_experience(full_text)),
            )
            mark_sent(job["source"], title, job.get("company", ""), link)
            new_count += 1
            total_new += 1
            time.sleep(1)  # Telegram rate-limit ke against thoda gap

        print(f"[main] {name}: {new_count} new jobs sent")

    print(f"=== Done. Total new jobs sent this run: {total_new} ===")
    return total_new


if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        # Agar poori script hi crash ho jaye to bhi ek Telegram alert mil jaye
        print(f"[main] FATAL ERROR: {e}")
        send_text(f"⚠️ QA Job Bot crashed: {e}")
        sys.exit(1)
