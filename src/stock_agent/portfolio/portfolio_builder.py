"""Build a simulated portfolio using Stock Ranker scores."""

from __future__ import annotations

import math


def build_portfolio(
    ranked_stocks: list[dict],
    budget: float,
    prices: dict[str, float],
    max_weight: float = 0.40,
) -> dict:
    """
    Allocate a budget according to stock ranking scores.

    No real trades are executed.
    """

    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    if not 0 < max_weight <= 1:
        raise ValueError("max_weight must be between 0 and 1.")

    if not ranked_stocks:
        raise ValueError("At least one ranked stock is required.")

    scores = {}

    for stock in ranked_stocks:
        ticker = stock["ticker"].strip().upper()
        score = float(stock["score"])

        if not ticker or ticker in scores:
            raise ValueError("Ticker symbols must be non-empty and unique.")

        if not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError("Stock scores must be between 0 and 100.")

        scores[ticker] = score

    if len(scores) * max_weight < 1:
        raise ValueError(
            "Not enough stocks to satisfy the maximum weight constraint."
        )

    eligible = {
        ticker: score
        for ticker, score in scores.items()
        if score > 0
    }

    if not eligible:
        raise ValueError("No stocks have a positive ranking score.")

    for ticker in eligible:
        if ticker not in prices:
            raise ValueError(f"Missing price for {ticker}.")

        price = float(prices[ticker])

        if not math.isfinite(price) or price <= 0:
            raise ValueError(f"Invalid price for {ticker}.")

    total_score = sum(eligible.values())

    weights = {
        ticker: score / total_score
        for ticker, score in eligible.items()
    }

    # Iteratively cap weights and redistribute excess.
    capped = set()

    while True:
        exceeded = [
            ticker
            for ticker, weight in weights.items()
            if ticker not in capped and weight > max_weight
        ]

        if not exceeded:
            break

        for ticker in exceeded:
            weights[ticker] = max_weight
            capped.add(ticker)

        remaining = 1.0 - sum(weights.values())
        uncapped = [
            ticker for ticker in weights
            if ticker not in capped
        ]

        if not uncapped:
            break

        remaining_score = sum(eligible[ticker] for ticker in uncapped)

        for ticker in uncapped:
            weights[ticker] = (
                remaining * eligible[ticker] / remaining_score
            )

    holdings = []
    total_invested = 0.0

    for ticker, weight in weights.items():
        allocation = budget * weight
        price = float(prices[ticker])
        shares = math.floor(allocation / price)
        invested = shares * price

        holdings.append({
            "ticker": ticker,
            "score": eligible[ticker],
            "weight": round(weight, 4),
            "allocated_budget": round(allocation, 2),
            "price": price,
            "shares": shares,
            "invested": round(invested, 2),
        })

        total_invested += invested

    holdings.sort(key=lambda item: (-item["weight"], item["ticker"]))

    return {
        "budget": round(budget, 2),
        "total_invested": round(total_invested, 2),
        "cash_remaining": round(budget - total_invested, 2),
        "holdings": holdings,
    }
