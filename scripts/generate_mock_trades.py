"""Generate a synthetic portfolio + returns history for testing."""
import argparse
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM",
           "XOM", "WMT", "JNJ", "V", "PG", "DIS", "NFLX"]
ASSET_CLASSES = {"AAPL": "equity", "MSFT": "equity", "GOOGL": "equity",
                 "AMZN": "equity", "NVDA": "equity", "TSLA": "equity",
                 "META": "equity", "JPM": "equity", "XOM": "equity",
                 "WMT": "equity", "JNJ": "equity", "V": "equity",
                 "PG": "equity", "DIS": "equity", "NFLX": "equity"}


def generate_portfolio(n_positions=500, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_positions):
        t = rng.choice(TICKERS)
        qty = int(rng.integers(10, 500))
        price = float(rng.uniform(50, 500))
        rows.append({
            "position_id": f"POS-{i:05d}",
            "ticker": t,
            "asset_class": ASSET_CLASSES[t],
            "quantity": qty,
            "price": round(price, 2),
            "market_value": round(qty * price, 2),
            "trade_date": (date(2026, 4, 23)).isoformat(),
        })
    return pd.DataFrame(rows)


def generate_returns(n_days=504, seed=42):
    """Simulate daily portfolio returns. ~2yrs of data."""
    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0004, scale=0.011, size=n_days)
    # Add a couple stress days
    returns[100] = -0.045
    returns[300] = -0.038
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(n_days)]
    return pd.DataFrame({"date": dates, "return": returns})


def generate_backtest_data(returns_df, confidence=0.99):
    """Rolling 252d VaR vs next-day P&L."""
    window = 252
    var_list, pnl_list, dates = [], [], []
    vals = returns_df["return"].values
    for i in range(window, len(vals) - 1):
        lookback = vals[i-window:i]
        var = -np.percentile(lookback, (1 - confidence) * 100)
        var_list.append(var)
        pnl_list.append(vals[i+1])
        dates.append(returns_df["date"].iloc[i+1])
    return pd.DataFrame({"date": dates, "var": var_list, "pnl": pnl_list})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-positions", type=int, default=500)
    ap.add_argument("--output", default="data")
    args = ap.parse_args()

    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)

    portfolio = generate_portfolio(args.n_positions)
    returns = generate_returns()
    backtest = generate_backtest_data(returns)

    portfolio.to_csv(out / "sample_portfolio.csv", index=False)
    returns.to_csv(out / "sample_returns.csv", index=False)
    backtest[["date", "var"]].to_csv(out / "sample_var.csv", index=False)
    backtest[["date", "pnl"]].to_csv(out / "sample_pnl.csv", index=False)

    print(f"✓ Portfolio:  {len(portfolio):,} positions, NAV ${portfolio.market_value.sum():,.2f}")
    print(f"✓ Returns:    {len(returns):,} days")
    print(f"✓ Backtest:   {len(backtest):,} days")


if __name__ == "__main__":
    main()
