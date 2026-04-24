"""
Value-at-Risk (VaR) computation.

Supports three methodologies:
  - historical      : empirical percentile of historical P&L
  - parametric      : normal distribution assumption
  - monte_carlo     : GBM simulation (default 10k paths)

Usage:
    python -m src.risk.var --portfolio data/sample_portfolio.csv \
                           --method monte_carlo \
                           --confidence 0.99 \
                           --horizon 1
"""
from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm


logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


@dataclass
class VaRResult:
    method: str
    confidence: float
    horizon_days: int
    portfolio_value: float
    var_dollar: float
    var_pct: float
    es_dollar: float
    es_pct: float
    n_simulations: int | None = None


def historical_var(returns: np.ndarray, portfolio_value: float,
                   confidence: float = 0.99, horizon: int = 1) -> VaRResult:
    alpha = 1 - confidence
    var_pct = -np.percentile(returns, alpha * 100) * np.sqrt(horizon)
    tail = returns[returns <= np.percentile(returns, alpha * 100)]
    es_pct = -tail.mean() * np.sqrt(horizon)
    return VaRResult("historical", confidence, horizon, portfolio_value,
                     portfolio_value * var_pct, var_pct,
                     portfolio_value * es_pct, es_pct)


def parametric_var(returns: np.ndarray, portfolio_value: float,
                   confidence: float = 0.99, horizon: int = 1) -> VaRResult:
    mu, sigma = returns.mean(), returns.std()
    z = norm.ppf(1 - confidence)
    var_pct = -(mu * horizon + z * sigma * np.sqrt(horizon))
    # ES for normal distribution
    phi_z = norm.pdf(z)
    es_pct = -(mu * horizon - sigma * np.sqrt(horizon) * phi_z / (1 - confidence))
    return VaRResult("parametric", confidence, horizon, portfolio_value,
                     portfolio_value * var_pct, var_pct,
                     portfolio_value * es_pct, es_pct)


def monte_carlo_var(returns: np.ndarray, portfolio_value: float,
                    confidence: float = 0.99, horizon: int = 1,
                    n_sims: int = 10_000, seed: int = 42) -> VaRResult:
    rng = np.random.default_rng(seed)
    mu, sigma = returns.mean(), returns.std()

    # Geometric Brownian Motion paths
    z = rng.standard_normal((n_sims, horizon))
    daily = mu + sigma * z
    cum_return = daily.sum(axis=1)  # simple aggregation; for GBM use log-returns
    losses = -cum_return * portfolio_value

    var_dollar = np.percentile(losses, confidence * 100)
    tail = losses[losses >= var_dollar]
    es_dollar = tail.mean() if len(tail) else var_dollar

    return VaRResult(
        "monte_carlo", confidence, horizon, portfolio_value,
        var_dollar, var_dollar / portfolio_value,
        es_dollar, es_dollar / portfolio_value,
        n_simulations=n_sims,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfolio", default="data/sample_portfolio.csv")
    ap.add_argument("--returns", default="data/sample_returns.csv")
    ap.add_argument("--method", choices=["historical", "parametric", "monte_carlo"],
                    default="monte_carlo")
    ap.add_argument("--confidence", type=float, default=0.99)
    ap.add_argument("--horizon", type=int, default=1)
    ap.add_argument("--n-sims", type=int, default=10_000)
    args = ap.parse_args()

    portfolio = pd.read_csv(args.portfolio)
    portfolio_value = float(portfolio["market_value"].sum())

    returns = pd.read_csv(args.returns)["return"].values

    if args.method == "historical":
        r = historical_var(returns, portfolio_value, args.confidence, args.horizon)
    elif args.method == "parametric":
        r = parametric_var(returns, portfolio_value, args.confidence, args.horizon)
    else:
        r = monte_carlo_var(returns, portfolio_value, args.confidence, args.horizon,
                            n_sims=args.n_sims)

    print(f"\nPortfolio Value:         ${r.portfolio_value:,.2f}")
    print(f"{int(r.horizon_days)}-day {int(r.confidence*100)}% VaR ({r.method}):  "
          f"${r.var_dollar:12,.2f}   ({r.var_pct*100:.2f}%)")
    print(f"{int(r.horizon_days)}-day {int(r.confidence*100)}% ES  ({r.method}):  "
          f"${r.es_dollar:12,.2f}   ({r.es_pct*100:.2f}%)")
    if r.n_simulations:
        print(f"Simulations:             {r.n_simulations:,}")


if __name__ == "__main__":
    main()
