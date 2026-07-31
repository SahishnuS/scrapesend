#!/usr/bin/env bash
# scripts/setup_dev.sh
# One-shot local development environment bootstrap.
# Run once after cloning: bash scripts/setup_dev.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo ""
echo "🤖 InternHunt — Dev Environment Setup"
echo "========================================="

# ── Check prerequisites ────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.12+ required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js 20+ required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm required"; exit 1; }

# ── Copy env template ──────────────────────────────────────────────────────
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example — fill in your secrets!"
else
    echo "ℹ️  .env already exists, skipping copy"
fi

# ── Backend virtual environment ────────────────────────────────────────────
echo ""
echo "📦 Setting up Python backend..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
playwright install chromium --with-deps
echo "✅ Backend dependencies installed"
cd "$ROOT"

# ── Frontend dependencies ──────────────────────────────────────────────────
echo ""
echo "📦 Setting up Next.js frontend..."
cd frontend
npm install --silent
echo "✅ Frontend dependencies installed"
cd "$ROOT"

# ── Pre-commit hooks ───────────────────────────────────────────────────────
echo ""
echo "🪝 Installing pre-commit hooks..."
source backend/.venv/bin/activate
pre-commit install
echo "✅ Pre-commit hooks installed"

# ── Done ───────────────────────────────────────────────────────────────────
echo ""
echo "🚀 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Supabase, Telegram, and Gmail credentials"
echo "  2. Backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "  3. Frontend: cd frontend && npm run dev"
echo "  4. Docs:     http://localhost:8000/docs"
echo ""
