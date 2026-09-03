# QA Job Alert Bot

LinkedIn, Naukri, Indeed aur Apna se **pichle 24 ghante** ke QA/Software
Testing jobs (≤5 years experience) dhundh ke Telegram pe direct apply
link bhejta hai. **Auto-apply nahi karta** - tum khud link khol ke apply
karoge, isliye account ban hone ka risk nahi hai.

---

## Step 1: Telegram Bot Banao (5 min)

1. Telegram pe **@BotFather** ko search karo, `/start` bhejo
2. `/newbot` bhejo, bot ka naam aur username do (username `_bot` se end hona chahiye)
3. Tumhe ek **token** milega jaisa: `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxx`
   - Ye `TELEGRAM_BOT_TOKEN` hai, safe rakho
4. Apne naye bot ko Telegram me search karo, use `/start` bhejo (bot ko "wake up" karna zaroori hai)
5. Apna **chat_id** nikalne ke liye browser me ye URL kholo (TOKEN apna waala daalo):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
6. Response me `"chat":{"id": 123456789, ...}` milega - wahi number `TELEGRAM_CHAT_ID` hai

---

## Step 2: Code GitHub pe Daalo

```bash
cd qa-job-bot
git init
git add .
git commit -m "QA job alert bot"
```

GitHub pe ek naya **private** repo banao aur push kar do:
```bash
git remote add origin https://github.com/<tumhara-username>/qa-job-bot.git
git branch -M main
git push -u origin main
```

---

## Step 3: Render pe Deploy Karo

### Option A: Blueprint se (sabse aasan - render.yaml already hai)
1. [render.com](https://render.com) pe login karo (GitHub se sign in kar sakte ho)
2. **New +** → **Blueprint** → apna GitHub repo select karo
3. Render `render.yaml` khud padh lega aur Cron Job bana dega
4. Deploy hone se pehle ye 2 Environment Variables daalo:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. **Apply** dabao

### Option B: Manually
1. **New +** → **Cron Job**
2. GitHub repo connect karo
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Schedule**: `*/30 * * * *` (har 30 min - chaho to `*/15 * * * *` bhi kar sakte ho)
4. Environment tab me `TELEGRAM_BOT_TOKEN` aur `TELEGRAM_CHAT_ID` add karo
5. Create Cron Job

> **Note**: Render Cron Jobs free tier me nahi aate (paid feature hai,
> lekin sabse cheap "Starter" plan काफी hai is chhote script ke liye,
> ~$1-7/month range). Agar bilkul free rakhna hai to alternative: **GitHub
> Actions** (scheduled workflow) - wo free hai. Bata dena agar wo version
> chahiye, main bana dunga.

---

## Step 4: Test Karo

Render pe deploy hone ke baad, Cron Job ke dashboard me **"Trigger Run"**
button se manually ek run chala ke dekho - Telegram pe kuch minutes me
message aana chahiye (agar us waqt koi matching job mile to).

Local pe test karna ho to:
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="tumhara_token"
export TELEGRAM_CHAT_ID="tumhara_chat_id"
python main.py
```

---

## Kaise kaam karta hai

- Har 30 min me **LinkedIn** check hoti hai (guest/public search endpoint - login ke bina)
- QA/Testing keyword match + "5 years se kam experience" filter lagta hai
- Jo job pehle kabhi nahi bheji gayi (SQLite dedup DB), sirf wahi Telegram pe aati hai
- Message format: Title, Company, Location, Experience, Source, Direct Link

## Sirf LinkedIn kyun (Naukri/Indeed/Apna disabled by design)

Testing ke dauraan pata chala ki teeno platforms modern anti-bot / JS-rendering protection use karte hai jo bina paid residential proxy + real browser ke bypass nahi hoti:
- **Naukri**: reCAPTCHA-gated API (HTTP 406)
- **Indeed**: Cloudflare Turnstile, specifically datacenter IPs (jaisa Render) ko block karta hai (HTTP 403)
- **Apna**: Listing pages JavaScript se render hoti hai, raw HTML me job links hote hi nahi

Inko fix karne ke liye paid scraping service (ScrapFly/Apify, ~$0.50-$8 per 1000 results) chahiye hogi - abhi ke liye in teeno ko intentionally skip kiya gaya hai. Code `scrapers/` folder me maujood hai agar future me try karna ho, bas `main.py` ke `SCRAPERS` list me wapas enable kar dena.

LinkedIn ka guest endpoint reliable hai aur bina kisi paid service ke consistently kaam karta hai - isliye yahi primary source hai.

## Cost kam rakhne ke liye

- Schedule `*/30 * * * *` se `*/60 * * * *` kar do agar Render cost kam karni ho
- SQLite DB har run ke saath persist nahi rahegi agar disk attach nahi kiya (Render Cron Jobs ephemeral filesystem use karte hai) - iska matlab **restart ke baad purani "already sent" history mit sakti hai** aur duplicate aa sakte hai. Isse bachne ke liye Render pe ek **Persistent Disk** attach karo (Render dashboard → Disks) aur `DB_PATH` env var ko us disk ke path pe point karo, jaise `/var/data/sent_jobs.db`.
