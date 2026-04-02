#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

pip install -q yfinance

cd "$SCRIPT_DIR"
python3 stock_notifier.py

git -C "$REPO_ROOT" config user.email "daily-stock-agent@claude.ai"
git -C "$REPO_ROOT" config user.name "Daily Stock Agent"
git -C "$REPO_ROOT" add stock_notifier/history/ stock_notifier/report.html
git -C "$REPO_ROOT" commit -m "Daily stock report $(date +%Y-%m-%d)" || echo "Nothing to commit"
git -C "$REPO_ROOT" push
