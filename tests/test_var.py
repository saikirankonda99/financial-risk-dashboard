import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from src.risk.var import historical_var, parametric_var, monte_carlo_var


def fake_returns(seed=1):
    rng = np.random.default_rng(seed)
    return rng.normal(0.0005, 0.01, 1000)


def test_historical_var_positive():
    r = historical_var(fake_returns(), portfolio_value=1_000_000, confidence=0.99)
    assert r.var_dollar > 0
    assert r.es_dollar >= r.var_dollar


def test_parametric_var_positive():
    r = parametric_var(fake_returns(), portfolio_value=1_000_000, confidence=0.99)
    assert r.var_dollar > 0


def test_monte_carlo_var_positive():
    r = monte_carlo_var(fake_returns(), portfolio_value=1_000_000,
                         confidence=0.99, n_sims=1000)
    assert r.var_dollar > 0
    assert r.n_simulations == 1000
