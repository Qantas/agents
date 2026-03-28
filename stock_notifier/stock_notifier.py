#!/usr/bin/env python3
import json
import os
from datetime import datetime
import yfinance as yf

BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
HISTORY_DIR = os.path.join(BASE_DIR, "history")

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def fetch_stocks(tickers):
    stocks = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            fast = t.fast_info
            info = t.info
            price = fast.last_price
            prev = fast.previous_close
            change = price - prev
            pct = (change / prev) * 100
            stocks.append({
                "ticker": ticker,
                "price": price,
                "change": change,
                "pct": pct,
                "pe": info.get("trailingPE"),
                "week52_high": fast.year_high,
                "week52_low": fast.year_low,
            })
        except Exception as e:
            print(f"Warning: could not fetch {ticker}: {e}")
    return sorted(stocks, key=lambda x: x["pct"], reverse=True)


def fmt_pe(val):
    return f"{val:.1f}" if val else "N/A"


def print_table(stocks, top_n=3):
    date_str = datetime.now().strftime("%A, %b %d %Y %H:%M")
    print(f"\n{BOLD}Stock Watchlist — {date_str}{RESET}")
    W = 80
    print("-" * W)
    print(f"{'Ticker':<10} {'Price':>9} {'Change':>10} {'%Chg':>8}  {'P/E':>6}  {'52W High':>9}  {'52W Low':>9}")
    print("-" * W)

    n = len(stocks)
    top_tickers = {s["ticker"] for s in stocks[:top_n] if s["pct"] > 0}
    bottom_tickers = {s["ticker"] for s in stocks[n - top_n:] if s["pct"] < 0}
    for s in sorted(stocks, key=lambda x: x["ticker"]):
        color = GREEN if s["change"] >= 0 else RED
        arrow = "▲" if s["change"] >= 0 else "▼"
        if s["ticker"] in top_tickers:
            label = f"{BOLD}{YELLOW}★ {s['ticker']:<8}{RESET}"
        elif s["ticker"] in bottom_tickers:
            label = f"{DIM}{CYAN}▽ {s['ticker']:<8}{RESET}"
        else:
            label = f"  {s['ticker']:<8}"
        print(
            f"{label} "
            f"${s['price']:>8.2f} "
            f"{color}{arrow} ${abs(s['change']):>6.2f} "
            f"{arrow}{abs(s['pct']):>5.2f}%{RESET}"
            f"  {fmt_pe(s['pe']):>6}"
            f"  ${s['week52_high']:>8.2f}"
            f"  ${s['week52_low']:>8.2f}"
        )

    print("-" * W)
    print(f"{YELLOW}★ Top {top_n} movers{RESET}  {DIM}{CYAN}▽ Bottom {top_n} movers{RESET}\n")


def save_history(stocks):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    date_key = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(HISTORY_DIR, f"{date_key}.json")
    existing = {}
    if os.path.exists(path):
        with open(path) as f:
            existing = json.load(f)
    existing.setdefault("date", date_key)
    existing.setdefault("generated_at", datetime.now().isoformat())
    existing.setdefault("stocks", {})
    for s in stocks:
        ticker = s["ticker"]
        existing["stocks"].setdefault(ticker, {}).update({
            "price": s["price"],
            "change": s["change"],
            "pct": s["pct"],
            "pe": s["pe"],
            "week52_high": s["week52_high"],
            "week52_low": s["week52_low"],
        })
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"[history] saved → {path}")
    files = sorted(f for f in os.listdir(HISTORY_DIR) if f.endswith(".json"))
    for old in files[:-10]:
        os.remove(os.path.join(HISTORY_DIR, old))


def main():
    config = load_config()
    stocks = fetch_stocks(config["watchlist"])
    if not stocks:
        print("No stock data retrieved.")
        return
    print_table(stocks)
    save_history(stocks)


if __name__ == "__main__":
    main()
