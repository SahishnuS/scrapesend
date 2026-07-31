# 🤖 RoboHunter AI

> Production-grade AI-powered internship monitoring and application management platform.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

---

## Overview

RoboHunter AI continuously monitors internship openings across Robotics, AI, Embedded Systems, Computer Vision, Autonomous Vehicles, Drones, IoT, Research Labs, and more. It detects new openings, matches them against your active resume with AI, sends instant notifications, and tracks your entire application lifecycle.

---

## Features

- 🔍 **24×7 Monitoring** — GitHub Actions crawls companies every hour
- 🤖 **AI Resume Matching** — Sentence Transformers cosine similarity scoring
- 📬 **Instant Notifications** — Telegram + Gmail SMTP
- 🗂️ **Application Tracking** — Full lifecycle with status history
- 📄 **Resume Manager** — Upload, activate, extract text
- 🏢 **Company Database** — CSV import/export, ATS-aware crawling
- 🎯 **ATS Handlers** — Greenhouse, Lever, Ashby, SmartRecruiters, Workable, and more
- 🖥️ **Application Assistant** — Playwright-assisted form filling (never auto-submits)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | Supabase PostgreSQL |
| Storage | Supabase Storage |
| AI | Sentence Transformers |
| Crawler | Playwright, BeautifulSoup |
| Notifications | Telegram Bot API, Gmail SMTP |
| Scheduler | GitHub Actions (hourly) |
| Deployment | Vercel (frontend), Railway/Fly.io (backend) |

---

## Project Structure

```
robot-hunter-ai/
├── frontend/          # Next.js App Router dashboard
├── backend/           # FastAPI REST API
├── playwright/        # Crawler + Application Assistant
├── scheduler/         # Orchestration entry points
├── docs/              # Architecture & API documentation
├── docker/            # Dockerfiles and compose
├── .github/           # GitHub Actions workflows
└── scripts/           # Utility and migration scripts
```

---

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Supabase account
- Telegram Bot (from @BotFather)
- Gmail App Password

### 1. Clone & Configure

```bash
git clone https://github.com/yourname/robot-hunter-ai.git
cd robot-hunter-ai
cp .env.example .env
# Fill in your secrets in .env
```

### 2. Start Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

### 4. Run Crawler Manually

```bash
cd scheduler
source ../.venv/bin/activate
python run_scheduler.py
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase service role key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat/channel ID |
| `SMTP_EMAIL` | Gmail address |
| `SMTP_APP_PASSWORD` | Gmail App Password (not your Gmail password) |
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

---

## Architecture

```
GitHub Actions (hourly)
    │
    ▼
Playwright Crawlers
    │
    ▼
ATS Detection & Job Extraction
    │
    ▼
Duplicate Detection (job_hash)
    │
    ▼
Supabase PostgreSQL
    │
    ▼
AI Matching (Sentence Transformers)
    │
    ▼
Notifications (Telegram + Gmail)
    │
    ▼
Next.js Dashboard
```

---

## Development Roadmap

- [x] Phase 1: Project Scaffolding
- [x] Phase 2: Database schema & migrations
- [x] Phase 3: Backend API
- [x] Phase 4: Frontend dashboard
- [x] Phase 5: Resume Manager
- [x] Phase 6: Categories & Companies
- [x] Phase 7: Crawler framework
- [x] Phase 8: ATS handlers
- [x] Phase 9: AI Matching
- [x] Phase 10: Notifications
- [x] Phase 11: GitHub Actions
- [x] Phase 12: Local Application Assistant
- [x] Phase 13: Testing
- [x] Phase 14: Documentation

---

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

## License

MIT © RoboHunter AI
