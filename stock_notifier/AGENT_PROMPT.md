You are running the daily stock report. The repo is already cloned in your working directory.

## Step 0 - Install dependencies
pip install -q yfinance

## Step 1 - Pull live stock data
cd stock_notifier && python3 stock_notifier.py

Capture per ticker: price, change $, change %, P/E, 52W high, 52W low. The script saves today's snapshot to history/YYYY-MM-DD.json.

## Step 2 - Load history and compute trends
Load all history files before today (up to 10):
  ls stock_notifier/history/ | sort | grep -v $(date +%Y-%m-%d)

If none exist, skip trends. Otherwise compute per ticker:
- price_delta_vs_yesterday, pct_delta_vs_yesterday
- streak: consecutive days moving same direction (up or down)
- momentum_5d: % change from oldest price in last 5 days to today
- avg_abs_move: mean of abs(pct) across all history days excluding today
- acceleration: abs(pct) > 1.5x avg_abs_move AND abs(pct) > 1%

Signal flags (can stack): BIG MOVE (abs pct > 3%), HOT STREAK (streak >= 3 up), COLD STREAK (streak >= 3 down), NEAR HIGH (price >= 99% of 52w high), NEAR LOW (price <= 101% of 52w low), ACCELERATING.

## Step 3 - Search for news
Web search each ticker: "TICKER stock news [current month year]"
Extract: key headlines, analyst upgrades/downgrades, notable developments, sentiment.

## Step 4 - Recommendations
For each stock write a 2-3 sentence summary and assign: Buy / Accumulate / Hold / Watch / Avoid.
Save recommendations into today's history file at stock_notifier/history/YYYY-MM-DD.json.

## Step 5 - Generate HTML report
Write to stock_notifier/report.html.

Color palette: bg #0f172a, card #1e293b, border #334155, green #4ade80/#14532d, red #f87171/#450a0a, amber #fef08a/#854d0e, cyan #67e8f9/#164e63, blue #93c5fd/#1c3456, purple #c4b5fd/#312e81, teal #5eead4/#134e4a. Font: -apple-system sans-serif.

Sections:
1. Header: "Stock Watchlist" + timestamp + subtitle (market open or closed)
2. Alerts banner (only if big moves or rec changes)
3. Click-to-sort table: Ticker / Price / Change / % / vs Yesterday / P/E / 52W High / 52W Low / Chart
   Charts: img src="https://finviz.com/chart.ashx?t=TICKER&ty=c&ta=0&p=d" with hover popup
4. Trends & Signals grid (skip if no history): compact cards sorted by flag count then alpha
5. Analysis cards: one per stock with price, P/E, 52W range, news summary, rec pill
6. Portfolio history table: last 10 days newest first, price + rec pill per ticker
7. Footer: disclaimer "For informational purposes only, not financial advice."

Include table sort script and chart hover popup script before </body>.

## Step 6 - Commit and push
ROOT=$(git rev-parse --show-toplevel)
git -C $ROOT config user.email daily-stock-agent@claude.ai
git -C $ROOT config user.name "Daily Stock Agent"
git -C $ROOT add stock_notifier/history/ stock_notifier/report.html
git -C $ROOT commit -m "Daily stock report $(date +%Y-%m-%d)"
git -C $ROOT push

Confirm when done.
