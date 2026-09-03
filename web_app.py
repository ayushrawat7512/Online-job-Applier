"""
Render ka FREE tier sirf "Web Service" type ko support karta hai (Cron Job
paid hai). Web Service ko ek zinda HTTP process chahiye hoti hai, isliye
hum ek chhota Flask server chala rahe hai jo:
  1. "/" route pe health-check jawab deta hai (OK)
  2. Background thread mein har 30 min pe run_once() (job checking) chalata hai

IMPORTANT LIMITATION: Render ka free web service 15 min tak koi HTTP
request na aane par "spin down" (so) ho jata hai. Sona hone par background
thread bhi ruk jata hai - matlab job-checking bhi ruk jayegi jab tak koi
naya HTTP request na aaye (jo service ko wapas "wake up" kar deta hai,
lekin usme 30-50 second lagte hai aur tab tak thread paused rehta hai).

FIX: Ek FREE external "uptime pinger" service use karo jo har 10-14 min
me tumhare Render URL ko ping kare, taaki wo kabhi so hi na paye:
  - UptimeRobot (uptimerobot.com) - free, 5 min interval tak
  - cron-job.org - free, koi bhi interval

Render se URL milte hi (jaisa https://qa-job-alert-web.onrender.com)
usko UptimeRobot/cron-job.org me daal dena - README me steps hai.
"""
import threading
import time
import os

from flask import Flask
from main import run_once

app = Flask(__name__)

CHECK_INTERVAL_SECONDS = 30 * 60  # 30 minute
_last_run_summary = {"last_run": None, "jobs_sent": 0, "runs_completed": 0}


def background_loop():
    while True:
        try:
            print("[web_app] Starting scheduled job check...")
            count = run_once()
            _last_run_summary["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            _last_run_summary["jobs_sent"] = count
            _last_run_summary["runs_completed"] += 1
        except Exception as e:
            print(f"[web_app] background_loop error: {e}")
        time.sleep(CHECK_INTERVAL_SECONDS)


@app.route("/")
def health():
    return {
        "status": "alive",
        "last_run": _last_run_summary["last_run"],
        "jobs_sent_last_run": _last_run_summary["jobs_sent"],
        "total_runs_completed": _last_run_summary["runs_completed"],
    }


# Background thread server start hote hi shuru ho jata hai (worker import
# hote waqt), taaki gunicorn ke andar bhi ye chale.
_thread = threading.Thread(target=background_loop, daemon=True)
_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
