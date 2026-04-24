"""Apply pre-defined stress scenarios to a portfolio."""
import pandas as pd


SCENARIOS = {
    "equity_crash_20pct":   {"equity": -0.20, "fx": 0.0,  "rates_bps": 0},
    "rate_hike_100bps":     {"equity": -0.05, "fx": 0.0,  "rates_bps": 100},
    "fx_shock":             {"equity": -0.02, "fx": -0.10, "rates_bps": 0},
    "pandemic_repeat":      {"equity": -0.35, "fx": -0.05, "rates_bps": -50},
}


def apply_stress(portfolio: pd.DataFrame, scenario: dict) -> dict:
    by_class = portfolio.groupby("asset_class")["market_value"].sum()
    equity = by_class.get("equity", 0)
    fx = by_class.get("fx", 0)
    bond = by_class.get("bond", 0)

    equity_pnl = equity * scenario["equity"]
    fx_pnl = fx * scenario["fx"]
    # Rough bond duration effect: 5yr duration assumption
    bond_pnl = -bond * 5 * (scenario["rates_bps"] / 10_000)

    return {
        "equity_pnl": round(equity_pnl, 2),
        "fx_pnl": round(fx_pnl, 2),
        "bond_pnl": round(bond_pnl, 2),
        "total_pnl": round(equity_pnl + fx_pnl + bond_pnl, 2),
    }


def run_all(portfolio: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, scenario in SCENARIOS.items():
        result = apply_stress(portfolio, scenario)
        result["scenario"] = name
        rows.append(result)
    return pd.DataFrame(rows).set_index("scenario")
