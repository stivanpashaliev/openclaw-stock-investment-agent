import pytest

from stock_agent.analysis import stock_ranker


def test_normalize_scores():
    result = stock_ranker._normalize_scores([0.10, 0.20, 0.30])

    assert result == pytest.approx([0, 50, 100])


def test_lower_values_get_higher_scores():
    result = stock_ranker._normalize_scores(
        [0.10, 0.20, 0.30],
        higher_is_better=False,
    )

    assert result == pytest.approx([100, 50, 0])


def test_equal_values_get_equal_scores():
    result = stock_ranker._normalize_scores([0.20, 0.20, 0.20])

    assert result == [100, 100, 100]


def test_rank_stocks_orders_by_weighted_score(monkeypatch):
    sample_data = {
        "AAA": {
            "ticker": "AAA",
            "total_return": 0.30,
            "annualized_volatility": 0.10,
            "max_drawdown": -0.05,
        },
        "BBB": {
            "ticker": "BBB",
            "total_return": 0.10,
            "annualized_volatility": 0.30,
            "max_drawdown": -0.20,
        },
        "CCC": {
            "ticker": "CCC",
            "total_return": 0.20,
            "annualized_volatility": 0.20,
            "max_drawdown": -0.10,
        },
    }

    def fake_analyze_stock(ticker, period="1y"):
        return sample_data[ticker]

    monkeypatch.setattr(
        stock_ranker,
        "analyze_stock",
        fake_analyze_stock,
    )

    result = stock_ranker.rank_stocks(["AAA", "BBB", "CCC"])

    assert [item["ticker"] for item in result] == ["AAA", "CCC", "BBB"]
    assert result[0]["score"] == 100.0
    assert result[1]["score"] == 54.17
    assert result[2]["score"] == 0.0


def test_empty_ticker_list_raises_error():
    with pytest.raises(ValueError):
        stock_ranker.rank_stocks([])
