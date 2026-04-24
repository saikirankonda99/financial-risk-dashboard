"""Forecast next-day volatility with a GARCH(1,1) model."""
import numpy as np
import pandas as pd


def forecast_vol(returns: pd.Series, horizon: int = 1) -> float:
    try:
        from arch import arch_model
    except ImportError:
        return float(returns.std())

    model = arch_model(returns * 100, vol="Garch", p=1, q=1, rescale=False)
    fit = model.fit(disp="off")
    forecast = fit.forecast(horizon=horizon, reindex=False)
    # Convert back from percent
    return float(np.sqrt(forecast.variance.values[-1, -1]) / 100)
