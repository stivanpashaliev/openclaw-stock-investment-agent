"""Performance metrics for historical portfolio backtests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_backtest_metrics(
    portfolio_values: pd.Series,
    periods_per_year: int = 252,
    risk_free_rate: float = 0.0,
) -> dict[str, float]:
    """
    Calculate performance and risk metrics for a backtested portfolio.

    Args:
        portfolio_values: Historical portfolio values in chronological order.
        periods_per_year: Number of trading periods in one year.
        risk_free_rate: Annual risk-free rate as a decimal.

    Returns:
        Dictionary containing portfolio performance metrics.
    """

    values = pd.to_numeric(
        portfolio_values,
        errors="coerce",
    ).dropna()

    if len(values) < 3:
        raise ValueError("At least two portfolio values are required.")

    if not np.isfinite(values).all():
        raise ValueError("Portfolio values must be finite.")

    if (values <= 0).any():
        raise ValueError("Portfolio values must be greater than zero.")

    if periods_per_year <= 0:
        raise ValueError("Periods per year must be greater than zero.")

    if not np.isfinite(risk_free_rate) or risk_free_rate <= -1:
        raise ValueError("Risk-free rate must be finite and greater than -1.")

    daily_returns = values.pct_change().dropna()

    total_return = values.iloc[-1] / values.iloc[0] - 1

    annualized_return = (
        (values.iloc[-1] / values.iloc[0])
        ** (periods_per_year / len(daily_returns))
        - 1
    )

    annualized_volatility = (
        daily_returns.std(ddof=1) * np.sqrt(periods_per_year)
    )

    running_max = values.cummax()
    drawdowns = values / running_max - 1
    max_drawdown = drawdowns.min()

    periodic_risk_free_rate = (
        (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    )

    excess_returns = daily_returns - periodic_risk_free_rate

    if daily_returns.std(ddof=1) == 0:
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = (
            excess_returns.mean()
            / daily_returns.std(ddof=1)
            * np.sqrt(periods_per_year)
        )

    return {
        "total_return": float(total_return),
        "annualized_return": float(annualized_return),
        "annualized_volatility": float(annualized_volatility),
        "max_drawdown": float(max_drawdown),
        "sharpe_ratio": float(sharpe_ratio),
    }
