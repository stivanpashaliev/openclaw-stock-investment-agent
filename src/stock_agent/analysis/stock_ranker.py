"""Rank stocks using transparent, weighted financial metrics."""

from __future__ import annotations

from stock_agent.analysis.stock_analysis import analyze_stock


WEIGHTS = {
    "total_return": 0.50,
    "annualized_volatility": 0.25,
    "max_drawdown": 0.25,
}


def _normalize_scores(
    values: list[float],
    higher_is_better: bool = True,
) -> list[float]:
    """Normalize metric values to a 0-100 scale."""
    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [100.0] * len(values)

    scores = []

    for value in values:
        if higher_is_better:
            score = (value - minimum) / (maximum - minimum)
        else:
            score = (maximum - value) / (maximum - minimum)

        scores.append(score * 100)

    return scores


def rank_stocks(
    tickers: list[str],
    period: str = "1y",
) -> list[dict]:
    """
    Rank stocks using return, volatility, and maximum drawdown.

    Scores are relative to the stocks in the supplied list.
    """
    if not tickers:
        raise ValueError("At least one ticker is required.")

    results = []

    for ticker in tickers:
        symbol = ticker.strip().upper()

        if not symbol:
            raise ValueError("Ticker symbols cannot be empty.")

        results.append(analyze_stock(symbol, period=period))

    return_scores = _normalize_scores(
        [item["total_return"] for item in results],
        higher_is_better=True,
    )

    volatility_scores = _normalize_scores(
        [item["annualized_volatility"] for item in results],
        higher_is_better=False,
    )

    drawdown_scores = _normalize_scores(
        [item["max_drawdown"] for item in results],
        higher_is_better=True,
    )

    for index, item in enumerate(results):
        score = (
            return_scores[index] * WEIGHTS["total_return"]
            + volatility_scores[index] * WEIGHTS["annualized_volatility"]
            + drawdown_scores[index] * WEIGHTS["max_drawdown"]
        )

        item["score"] = round(score, 2)

    return sorted(
        results,
        key=lambda item: (-item["score"], item["ticker"]),
    )
