"""Backtesting engine for historical portfolio simulations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from stock_agent.backtesting.metrics import calculate_backtest_metrics


def calculate_portfolio_value(
    prices: pd.DataFrame,
    weights: dict[str, float],
    initial_capital: float = 10_000.0,
) -> pd.Series:
    """
    Calculate historical portfolio value using fixed target weights.

    Assumes daily rebalancing to the specified weights.
    """

    if prices.empty:
        raise ValueError("Price data cannot be empty.")

    if not np.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("Initial capital must be finite and greater than zero.")

    if not weights:
        raise ValueError("Portfolio weights cannot be empty.")

    tickers = list(weights.keys())

    if any(not isinstance(ticker, str) or not ticker.strip() for ticker in tickers):
        raise ValueError("Ticker symbols must be non-empty strings.")

    if not set(tickers).issubset(prices.columns):
        raise ValueError("Price data is missing one or more portfolio tickers.")

    weight_values = list(weights.values())

    if any(
        not isinstance(weight, (int, float, np.number))
        or not np.isfinite(weight)
        for weight in weight_values
    ):
        raise ValueError("Portfolio weights must be finite numeric values.")

    if any(weight < 0 for weight in weight_values):
        raise ValueError("Portfolio weights cannot be negative.")

    total_weight = sum(weight_values)

    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError("Portfolio weights must sum to 1.")

    if prices.index.has_duplicates:
        raise ValueError("Price data cannot contain duplicate dates.")

    if not prices.index.is_monotonic_increasing:
        raise ValueError("Price data must be sorted chronologically.")

    portfolio_prices = prices[tickers].copy()

    portfolio_prices = portfolio_prices.apply(
        pd.to_numeric,
        errors="coerce",
    )

    if portfolio_prices.isna().any().any():
        raise ValueError("Price data cannot contain missing or non-numeric values.")

    if not np.isfinite(portfolio_prices.to_numpy()).all():
        raise ValueError("Price data must contain finite values.")

    if (portfolio_prices <= 0).any().any():
        raise ValueError("Prices must be greater than zero.")

    daily_returns = portfolio_prices.pct_change().dropna()

    weight_series = pd.Series(weights, dtype=float)

    portfolio_returns = daily_returns.dot(weight_series)

    portfolio_values = initial_capital * (1 + portfolio_returns).cumprod()

    first_date = portfolio_prices.index[0]

    portfolio_values.loc[first_date] = initial_capital

    return portfolio_values.sort_index()


def run_backtest(
    prices: pd.DataFrame,
    weights: dict[str, float],
    initial_capital: float = 10_000.0,
) -> dict:
    """Run a complete historical portfolio backtest."""

    portfolio_values = calculate_portfolio_value(
        prices=prices,
        weights=weights,
        initial_capital=initial_capital,
    )

    metrics = calculate_backtest_metrics(portfolio_values)

    return {
        "initial_capital": float(initial_capital),
        "final_value": float(portfolio_values.iloc[-1]),
        "portfolio_values": portfolio_values,
        "metrics": metrics,
    }
