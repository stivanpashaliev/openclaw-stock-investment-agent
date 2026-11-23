"""Core financial metrics calculated deterministically with Python."""

from __future__ import annotations

import numpy as np
import pandas as pd


def analyze_prices(close: pd.Series) -> dict[str, float]:
    """
    Calculate total return, annualized volatility, and maximum drawdown.

    Args:
        close: Series of historical closing prices.

    Returns:
        Dictionary of financial metrics as decimal values.

    Raises:
        ValueError: If prices are insufficient, invalid, or non-positive.
    """
    prices = pd.to_numeric(close, errors="coerce").dropna()

    if len(prices) < 2:
        raise ValueError("At least two valid closing prices are required.")

    if not np.isfinite(prices).all():
        raise ValueError("Prices must be finite numbers.")

    if (prices <= 0).any():
        raise ValueError("Prices must be greater than zero.")

    daily_returns = prices.pct_change().dropna()

    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
    annualized_volatility = daily_returns.std(ddof=1) * np.sqrt(252)

    running_max = prices.cummax()
    drawdowns = (prices / running_max) - 1
    max_drawdown = drawdowns.min()

    return {
        "total_return": float(total_return),
        "annualized_volatility": float(annualized_volatility),
        "max_drawdown": float(max_drawdown),
    }
