import pandas as pd
import pytest

from stock_agent.analysis.metrics import analyze_prices


def test_known_return_and_drawdown():
    prices = pd.Series([100, 110, 105, 120])

    result = analyze_prices(prices)

    assert result["total_return"] == pytest.approx(0.20)
    assert result["max_drawdown"] == pytest.approx(-5 / 110)
    assert result["annualized_volatility"] > 0


def test_constant_prices_have_zero_return_and_volatility():
    prices = pd.Series([100, 100, 100, 100, 100])

    result = analyze_prices(prices)

    assert result["total_return"] == pytest.approx(0.0)
    assert result["annualized_volatility"] == pytest.approx(0.0)
    assert result["max_drawdown"] == pytest.approx(0.0)


def test_insufficient_prices_raise_error():
    with pytest.raises(ValueError):
        analyze_prices(pd.Series([100]))


def test_zero_price_raises_error():
    with pytest.raises(ValueError):
        analyze_prices(pd.Series([100, 0, 110]))


def test_negative_price_raises_error():
    with pytest.raises(ValueError):
        analyze_prices(pd.Series([100, -5, 110]))
