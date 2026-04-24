"""Aggregate intraday transactions into end-of-day positions."""
import pandas as pd


def aggregate_positions(trades: pd.DataFrame) -> pd.DataFrame:
    return (
        trades
        .groupby(["trade_date", "ticker", "asset_class"], as_index=False)
        .agg(
            quantity=("quantity", "sum"),
            market_value=("market_value", "sum"),
            avg_price=("price", "mean"),
        )
    )
