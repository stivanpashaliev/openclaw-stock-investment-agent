import pandas as pd
import pytest

from stock_agent.backtesting.engine import (
    calculate_portfolio_value,
    run_backtest,
)


def test_calculate_portfolio_value():
    prices = pd.DataFrame({
        "AAPL": [100, 110, 121],
        "MSFT": [100, 100, 110],
    })

    weights = {"AAPL": 0.6, "MSFT": 0.4}

    result = calculate_portfolio_value(
        prices,
        weights,
        initial_capital=10_000,
    )

    assert result.iloc[0] == pytest.approx(10_000)
    assert result.iloc[-1] == pytest.approx(11_660)


def test_constant_prices_preserve_capital():
    prices = pd.DataFrame({
        "AAPL": [100, 100, 100],
        "MSFT": [50, 50, 50],
    })

    weights = {"AAPL": 0.5, "MSFT": 0.5}

    result = calculate_portfolio_value(prices, weights)

    assert result.iloc[-1] == pytest.approx(10_000)


def test_invalid_weights_raise_error():
    prices = pd.DataFrame({
        "AAPL": [100, 110],
        "MSFT": [100, 105],
    })

    weights = {"AAPL": 0.6, "MSFT": 0.3}

    with pytest.raises(ValueError):
        calculate_portfolio_value(prices, weights)


def test_missing_ticker_raises_error():
    prices = pd.DataFrame({
        "AAPL": [100, 110],
    })

    weights = {"AAPL": 0.5, "MSFT": 0.5}

    with pytest.raises(ValueError):
        calculate_portfolio_value(prices, weights)


def test_empty_prices_raise_error():
    prices = pd.DataFrame()
    weights = {"AAPL": 1.0}

    with pytest.raises(ValueError):
        calculate_portfolio_value(prices, weights)

def test_run_backtest_returns_complete_results():
    prices = pd.DataFrame({
        "AAPL": [100, 110, 121],
        "MSFT": [100, 100, 110],
    })

    weights = {"AAPL": 0.6, "MSFT": 0.4}

    result = run_backtest(
        prices=prices,
        weights=weights,
        initial_capital=10_000,
    )

    assert result["initial_capital"] == pytest.approx(10_000)
    assert result["final_value"] == pytest.approx(11_660)

    assert "portfolio_values" in result
    assert "metrics" in result

    assert result["metrics"]["total_return"] == pytest.approx(0.166)

def test_nan_weight_raises_error():
    prices = pd.DataFrame({
        "AAPL": [100, 110, 120],
        "MSFT": [100, 105, 110],
    })

    weights = {"AAPL": float("nan"), "MSFT": float("nan")}

    with pytest.raises(ValueError):
        calculate_portfolio_value(prices, weights)


def test_infinite_initial_capital_raises_error():
    prices = pd.DataFrame({
        "AAPL": [100, 110, 120],
    })

    weights = {"AAPL": 1.0}

    with pytest.raises(ValueError):
        calculate_portfolio_value(
            prices,
            weights,
            initial_capital=float("inf"),
        )


def test_duplicate_dates_raise_error():
    dates = pd.to_datetime([
        "2026-01-01",
        "2026-01-02",
        "2026-01-02",
    ])

    prices = pd.DataFrame(
        {"AAPL": [100, 110, 120]},
        index=dates,
    )

    weights = {"AAPL": 1.0}

    with pytest.raises(ValueError, match="duplicate dates"):
        calculate_portfolio_value(prices, weights)


def test_unsorted_dates_raise_error():
    dates = pd.to_datetime([
        "2026-01-03",
        "2026-01-01",
        "2026-01-02",
    ])

    prices = pd.DataFrame(
        {"AAPL": [120, 100, 110]},
        index=dates,
    )

    weights = {"AAPL": 1.0}

    with pytest.raises(ValueError, match="chronologically"):
        calculate_portfolio_value(prices, weights)
