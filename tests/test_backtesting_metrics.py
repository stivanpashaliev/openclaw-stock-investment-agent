import pandas as pd
import pytest

from stock_agent.backtesting.metrics import calculate_backtest_metrics


def test_known_portfolio_metrics():
    values = pd.Series([10000, 11000, 9900, 12000])

    result = calculate_backtest_metrics(values)

    assert result["total_return"] == pytest.approx(0.20)
    assert result["max_drawdown"] == pytest.approx(-0.10)
    assert result["annualized_volatility"] > 0
    assert result["sharpe_ratio"] != 0


def test_constant_portfolio_values():
    values = pd.Series([10000, 10000, 10000, 10000])

    result = calculate_backtest_metrics(values)

    assert result["total_return"] == pytest.approx(0.0)
    assert result["annualized_volatility"] == pytest.approx(0.0)
    assert result["max_drawdown"] == pytest.approx(0.0)
    assert result["sharpe_ratio"] == 0.0


def test_insufficient_values_raise_error():
    values = pd.Series([10000, 11000])

    with pytest.raises(ValueError):
        calculate_backtest_metrics(values)


def test_zero_values_raise_error():
    values = pd.Series([10000, 0, 11000])

    with pytest.raises(ValueError):
        calculate_backtest_metrics(values)


def test_invalid_periods_per_year_raise_error():
    values = pd.Series([10000, 10500, 11000])

    with pytest.raises(ValueError):
        calculate_backtest_metrics(values, periods_per_year=0)
