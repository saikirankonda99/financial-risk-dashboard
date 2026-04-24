"""
Backtest VaR model accuracy.

Computes:
  - Breach count vs. expected
  - Kupiec POF (proportion of failures) test
  - Christoffersen conditional coverage test (independence)
"""
import argparse

import numpy as np
import pandas as pd
from scipy.stats import chi2


def kupiec_pof(breaches: int, total: int, alpha: float = 0.01) -> dict:
    """Kupiec proportion-of-failures likelihood ratio test."""
    p_hat = breaches / total
    if breaches == 0 or breaches == total:
        return {"statistic": None, "p_value": None}
    lr = -2 * np.log(
        ((1 - alpha) ** (total - breaches) * alpha ** breaches)
        / ((1 - p_hat) ** (total - breaches) * p_hat ** breaches)
    )
    return {"statistic": lr, "p_value": 1 - chi2.cdf(lr, df=1)}


def christoffersen(breach_series: np.ndarray) -> dict:
    """Christoffersen independence test - are breaches i.i.d?"""
    n00 = n01 = n10 = n11 = 0
    for i in range(1, len(breach_series)):
        prev, curr = int(breach_series[i-1]), int(breach_series[i])
        if prev == 0 and curr == 0: n00 += 1
        elif prev == 0 and curr == 1: n01 += 1
        elif prev == 1 and curr == 0: n10 += 1
        elif prev == 1 and curr == 1: n11 += 1

    if (n00 + n01) == 0 or (n10 + n11) == 0:
        return {"statistic": None, "p_value": None}
    pi01 = n01 / (n00 + n01)
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    if pi in (0, 1) or pi11 in (0, 1):
        return {"statistic": None, "p_value": None}

    lr = -2 * (
        (n00 + n10) * np.log(1 - pi) + (n01 + n11) * np.log(pi)
        - n00 * np.log(1 - pi01) - n01 * np.log(pi01)
        - n10 * np.log(1 - pi11) - n11 * np.log(pi11)
    )
    return {"statistic": lr, "p_value": 1 - chi2.cdf(lr, df=1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pnl-file", default="data/sample_pnl.csv")
    ap.add_argument("--var-file", default="data/sample_var.csv")
    ap.add_argument("--confidence", type=float, default=0.99)
    args = ap.parse_args()

    try:
        pnl = pd.read_csv(args.pnl_file)["pnl"].values
        var_series = pd.read_csv(args.var_file)["var"].values
    except FileNotFoundError:
        print("Backtest data not found; run generate_mock_trades.py first")
        return

    breaches = (pnl < -var_series).astype(int)
    n = len(breaches)
    n_breaches = int(breaches.sum())
    expected = (1 - args.confidence) * n

    kup = kupiec_pof(n_breaches, n, 1 - args.confidence)
    chr = christoffersen(breaches)

    print(f"Backtest window:    {n} days")
    print(f"Breaches (observed): {n_breaches}")
    print(f"Breaches (expected): {expected:.1f}")
    print(f"Breach rate:         {n_breaches/n*100:.2f}%")
    print(f"Kupiec POF p-value:  {kup['p_value']:.3f}" if kup["p_value"] else "Kupiec POF: undefined")
    print(f"Christoffersen p-value: {chr['p_value']:.3f}" if chr["p_value"] else "Christoffersen: undefined")


if __name__ == "__main__":
    main()
