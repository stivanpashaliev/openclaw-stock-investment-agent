import pytest

from stock_agent.portfolio.portfolio_builder import build_portfolio


def test_build_portfolio_allocates_budget():
    ranked_stocks = [
        {"ticker": "AAPL", "score": 100},
        {"ticker": "AMZN", "score": 50},
        {"ticker": "MSFT", "score": 25},
    ]

    prices = {
        "AAPL": 100,
        "AMZN": 50,
        "MSFT": 25,
    }

    result = build_portfolio(ranked_stocks, 10000, prices)

    assert result["budget"] == 10000
    assert result["total_invested"] <= 10000
    assert result["cash_remaining"] >= 0
    assert len(result["holdings"]) == 3


def test_maximum_weight_is_respected():
    ranked_stocks = [
        {"ticker": "AAPL", "score": 100},
        {"ticker": "AMZN", "score": 50},
        {"ticker": "MSFT", "score": 25},
    ]

    prices = {
        "AAPL": 100,
        "AMZN": 50,
        "MSFT": 25,
    }

    result = build_portfolio(ranked_stocks, 10000, prices)

    for holding in result["holdings"]:
        assert holding["weight"] <= 0.40


def test_zero_score_stock_is_excluded():
    ranked_stocks = [
        {"ticker": "AAPL", "score": 100},
        {"ticker": "NVDA", "score": 0},
        {"ticker": "MSFT", "score": 50},
    ]

    prices = {
        "AAPL": 100,
        "NVDA": 200,
        "MSFT": 50,
    }

    result = build_portfolio(ranked_stocks, 10000, prices)

    tickers = [item["ticker"] for item in result["holdings"]]

    assert "NVDA" not in tickers


def test_invalid_budget_raises_error():
    with pytest.raises(ValueError):
        build_portfolio(
            [{"ticker": "AAPL", "score": 100}],
            0,
            {"AAPL": 100},
        )


def test_insufficient_stocks_for_weight_limit():
    with pytest.raises(ValueError):
        build_portfolio(
            [{"ticker": "AAPL", "score": 100}],
            10000,
            {"AAPL": 100},
        )


def test_no_positive_scores_raises_error():
    with pytest.raises(ValueError):
        build_portfolio(
            [{"ticker": "AAPL", "score": 0},
             {"ticker": "MSFT", "score": 0},
             {"ticker": "AMZN", "score": 0}],
            10000,
            {"AAPL": 100, "MSFT": 100, "AMZN": 100},
        )
