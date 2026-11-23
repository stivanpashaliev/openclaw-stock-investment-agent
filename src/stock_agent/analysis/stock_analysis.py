"""Combine market data collection and financial metrics."""

from stock_agent.data.market_data import get_historical_prices
from stock_agent.analysis.metrics import analyze_prices


def analyze_stock(ticker: str, period: str = "1y") -> dict:
    """Fetch market data and calculate core investment metrics."""
    data = get_historical_prices(ticker, period=period)
    metrics = analyze_prices(data["close"])

    return {
        "ticker": ticker.strip().upper(),
        "period": period,
        "data_points": len(data),
        "start_date": str(data.index[0])[:10],
        "end_date": str(data.index[-1])[:10],
        **metrics,
    }
