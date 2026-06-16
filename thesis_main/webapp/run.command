#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Metro Cebu Valuation webapp — one-click launcher.
#
#   Double-click this file in Finder, OR run from a terminal:
#       ./run.command
#
# It starts BOTH processes the app needs and stops them together on Ctrl+C:
#   1. FastAPI inference backend  -> http://127.0.0.1:8000   (Property Predictor)
#   2. Vite frontend (Leaflet UI) -> http://127.0.0.1:5173   (opens in browser)
#
# Flags:
#   --export   force a re-export of the static JSON/GeoJSON before launching
#              (normally skipped — the thesis data is frozen and already exported)
# ---------------------------------------------------------------------------
set -uo pipefail

# Always run from the webapp/ folder, regardless of where it was launched from.
cd "$(dirname "$0")" || exit 1
HERE="$(pwd)"
VENV_PY="$HERE/../../.venv/bin/python"

echo "Metro Cebu Valuation webapp"
echo "==========================="

# --- sanity checks --------------------------------------------------------
if [ ! -x "$VENV_PY" ]; then
  echo "ERROR: thesis venv python not found at $VENV_PY" >&2
  echo "       (expected the project .venv two levels up from webapp/)" >&2
  exit 1
fi
command -v npm >/dev/null 2>&1 || { echo "ERROR: npm not found on PATH" >&2; exit 1; }

# --- frontend deps (first run only) --------------------------------------
if [ ! -d node_modules/vite ]; then
  echo "Installing frontend dependencies (first run only)…"
  npm install || { echo "ERROR: npm install failed" >&2; exit 1; }
fi

# --- static data (skip unless missing or --export) -----------------------
if [ "${1:-}" = "--export" ] || [ ! -f public/data/listings.json ] || [ ! -f public/data/barangay_features.json ]; then
  echo "Exporting static data from the frozen ABT + price surfaces…"
  npm run export:data || echo "WARNING: data export failed — map views may be stale" >&2
fi

# --- backend (FastAPI / uvicorn) -----------------------------------------
# Reuse an already-running backend if one is healthy on 8000 (avoids the
# "address already in use" error and double-launches). Only kill on exit the
# backend THIS script started.
API_PID=""
OWN_BACKEND=0
if curl -fs http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
  echo "Backend already running     -> http://127.0.0.1:8000 (reusing it)"
else
  echo "Starting inference backend  -> http://127.0.0.1:8000"
  WEBAPP_API=1 "$VENV_PY" -m uvicorn api.main:app \
    --host 127.0.0.1 --port 8000 --log-level warning &
  API_PID=$!
  OWN_BACKEND=1
fi

# Stop our backend whenever this script exits (Ctrl+C, or the frontend quits).
cleanup() {
  if [ "$OWN_BACKEND" = "1" ] && [ -n "$API_PID" ]; then
    echo
    echo "Stopping backend (pid $API_PID)…"
    kill "$API_PID" 2>/dev/null
    wait "$API_PID" 2>/dev/null
  fi
}
trap cleanup EXIT INT TERM

# --- wait for the backend we started to answer (max ~20s; non-fatal) ------
if [ "$OWN_BACKEND" = "1" ]; then
  printf "Waiting for backend"
  for _ in $(seq 1 20); do
    if curl -fs http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
      printf " ready.\n"; break
    fi
    if ! kill -0 "$API_PID" 2>/dev/null; then
      printf "\nWARNING: backend exited early — the Predictor page will not work,\n"
      printf "         but the Market Map and Price Surface still render.\n"
      break
    fi
    printf "."; sleep 1
  done
fi

# --- frontend (foreground; Ctrl+C here stops everything) -----------------
echo "Starting frontend           -> http://127.0.0.1:5173   (Ctrl+C to stop both)"
npm run dev -- --open
