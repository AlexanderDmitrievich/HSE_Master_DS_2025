#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ -f myvenv/bin/activate ]; then
  # shellcheck source=/dev/null
  source myvenv/bin/activate
fi

python utils/init_db.py

python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

streamlit run frontend/Main.py --server.port 8501

kill "$API_PID" 2>/dev/null || true
