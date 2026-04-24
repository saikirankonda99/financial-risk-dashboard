"""
Monte Carlo simulation for multi-asset portfolios.

Uses Cholesky decomposition of the correlation matrix to preserve co-movement
across positions during simulation.
"""
import numpy as np
import pandas as pd


def simulate_portfolio(
    weights: np.ndarray,
    mu: np.ndarray,
    cov: np.ndarray,
    horizon: int = 1,
    n_sims: int = 10_000,
    seed: int = 42,
) -> np.ndarray:
    """Simulate portfolio returns via correlated GBM.

    Returns an array of shape (n_sims,) of portfolio-level aggregated returns.
    """
    rng = np.random.default_rng(seed)
    L = np.linalg.cholesky(cov)
    z = rng.standard_normal((n_sims, len(weights), horizon))
    correlated = np.einsum("ij,skj->sik", L, z)
    # daily returns per asset per sim
    asset_returns = mu.reshape(-1, 1) + correlated
    # aggregate across time
    cumulative = asset_returns.sum(axis=2)
    # portfolio return weighted
    return cumulative @ weights
