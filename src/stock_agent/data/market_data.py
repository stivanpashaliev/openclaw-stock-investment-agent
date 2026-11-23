"""Fetch historical market data from Yahoo Finance using yfinance."""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def get_historical_prices(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Download historical prices for a stock ticker.

    Args:
        ticker: Stock symbol, e.g. AAPL or MSFT.
        period: Historical period, e.g. 1mo, 3mo, 6mo, 1y, 2y, 5y.
        interval: Data frequency, e.g. 1d, 1wk, 1mo.

    Returns:
        DataFrame with historical OHLCV data.

    Raises:
        ValueError: If the ticker is invalid or no data is returned.
    """
    symbol = ticker.strip().upper()

    if not symbol:
        raise ValueError("Ticker symbol cannot be empty.")

    data = yf.Ticker(symbol).history(
        period=period,
        interval=interval,
        auto_adjust=True,
    )

    if data.empty:
        raise ValueError(f"No market data returned for ticker '{symbol}'.")

    if "Close" not in data.columns:
        raise ValueError(f"Market data for '{symbol}' is missing the Close column.")

    data.columns = [column.lower() for column in data.columns]
    data.index.name = "date"

    return data
