# 🤖 RoboHunter AI

> **A production-grade, fully automated AI-powered internship monitoring and application management platform.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

RoboHunter AI is an autonomous agent that continuously scours the internet for internship and new-grad openings across deep-tech industries (Robotics, AI, Embedded Systems, Computer Vision, Autonomous Vehicles, and IoT). 

It automatically detects new positions, uses **Natural Language Processing (NLP)** to score the job description against your active resume, and beams a high-priority alert directly to your phone (via Telegram and Email) if it detects a strong match. Never manually hunt for a job board again.

---

## ✨ Key Features

- **🌐 24×7 Cloud Automation** — Fully headless Playwright crawler runs on GitHub Actions every 2 hours.
- **🧠 AI Resume Matching** — Uses `SentenceTransformers` and cosine similarity to dynamically calculate how well your resume matches the job description.
- **🎯 ATS-Aware Crawling** — Intelligently parses specific ATS layouts (Greenhouse, Lever, Workable, etc.) to extract clean data.
- **📬 Instant Mobile Alerts** — Real-time push notifications delivered via Telegram Bot API and Gmail SMTP.
- **📊 Beautiful Dashboard** — Manage companies, track applications, and view cloud logs in a sleek Next.js dark-mode UI.
- **📂 Bulk Management** — Drag-and-drop CSV uploads to track hundreds of target companies instantly.

---

## 🛠️ Architecture Stack

| Layer | Technology |
|-------|-----------|
| **Frontend UI** | Next.js 15, React, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | FastAPI, SQLAlchemy (Async), Alembic, Pydantic |
| **Database** | PostgreSQL hosted on Supabase |
| **AI / NLP** | `all-MiniLM-L6-v2` via SentenceTransformers |
| **Web Crawler** | Playwright (Headless Chromium), BeautifulSoup4 |
| **CI / CD Pipeline**| GitHub Actions (Cron Scheduling & Automation) |

### System Flow
1. **GitHub Actions** wakes up every 2 hours and boots the Python orchestrator (`scripts/monitor.py`).
2. **Playwright** crawls all active companies in the Supabase DB to find new URLs.
3. The **AI Matcher** compares new job descriptions against your active Resume text.
4. If the `match_score` exceeds the 15% threshold, the **Notifier** pushes a Telegram & Email alert.
5. The **Next.js Dashboard** fetches the latest data from the FastAPI backend for manual review.

---

## 🚀 Setup & Installation

### 1. Prerequisites
- Node.js 20+
- Python 3.12+
- A [Supabase](https://supabase.com/) account (Free tier)
- A Telegram Bot Token (from `@BotFather`)
- A Gmail App Password

### 2. Clone the Repository
```bash
git clone https://github.com/SahishnuS/scrapesend.git
cd scrapesend/robot-hunter-ai
cp .env.example .env
```

### 3. Local Development (Backend & Frontend)

To run the Next.js Dashboard locally:

**Terminal 1 (Backend):**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000/dashboard` in your browser.

---

## ☁️ Cloud Automation Deployment

RoboHunter AI is designed to run in the background forever without keeping your laptop open. 

1. Push this code to your GitHub Repository.
2. Go to your repository on GitHub -> **Settings** -> **Secrets and variables** -> **Actions**.
3. Add the following 7 Repository Secrets (values found in your `.env`):
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `DATABASE_URL`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `SMTP_EMAIL`
   - `SMTP_APP_PASSWORD`
4. Go to the **Actions** tab on GitHub, click **"RoboHunter AI Automated Monitor"**, and click **Run workflow**.

The cloud system will now autonomously scrape and notify you of high-matching jobs every 2 hours!

---

## 📝 License
This project is licensed under the MIT License.
