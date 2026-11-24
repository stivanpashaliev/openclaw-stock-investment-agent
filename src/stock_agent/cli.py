
"""Command-line interface for the Stock Investment Agent."""

from __future__ import annotations

import argparse
import json
import sys

from stock_agent.analysis.stock_analysis import analyze_stock
from stock_agent.analysis.stock_ranker import rank_stocks
from stock_agent.data.market_data import get_historical_prices
from stock_agent.portfolio.portfolio_builder import build_portfolio
from stock_agent.backtesting.engine import run_backtest


def output_json(data: dict) -> None:
    """Print results as JSON."""
    print(json.dumps(data, indent=2, default=str))


def parse_tickers(value: str) -> list[str]:
    """Parse comma-separated ticker symbols."""
    tickers = [ticker.strip().upper() for ticker in value.split(",")]
    tickers = [ticker for ticker in tickers if ticker]

    if not tickers:
        raise ValueError("At least one ticker is required.")

    if len(tickers) != len(set(tickers)):
        raise ValueError("Ticker symbols must be unique.")

    return tickers


def handle_analyze(args: argparse.Namespace) -> None:
    result = analyze_stock(args.ticker, period=args.period)
    output_json(result)


def handle_rank(args: argparse.Namespace) -> None:
    tickers = parse_tickers(args.tickers)
    results = rank_stocks(tickers, period=args.period)
    output_json({"ranked_stocks": results})


def handle_portfolio(args: argparse.Namespace) -> None:
    tickers = parse_tickers(args.tickers)
    ranked = rank_stocks(tickers, period=args.period)

    prices = {}
    for ticker in tickers:
        data = get_historical_prices(ticker, period="5d")
        prices[ticker] = float(data["close"].iloc[-1])

    result = build_portfolio(
        ranked_stocks=ranked,
        budget=args.budget,
        prices=prices,
        max_weight=args.max_weight,
    )
    output_json(result)


def handle_backtest(args: argparse.Namespace) -> None:
    tickers = parse_tickers(args.tickers)
    ranked = rank_stocks(tickers, period=args.period)

    positive = [stock for stock in ranked if stock["score"] > 0]
    if not positive:
        raise ValueError("No stocks have positive ranking scores.")

    total_score = sum(stock["score"] for stock in positive)
    weights = {
        stock["ticker"]: stock["score"] / total_score
        for stock in positive
    }

    price_data = {}
    for ticker in weights:
        data = get_historical_prices(ticker, period=args.period)
        price_data[ticker] = data["close"]

    import pandas as pd

    prices = pd.DataFrame(price_data).dropna()

    result = run_backtest(
        prices=prices,
        weights=weights,
        initial_capital=args.capital,
    )

    result["portfolio_values"] = [
        {"date": str(date)[:10], "value": float(value)}
        for date, value in result["portfolio_values"].items()
    ]

    output_json(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stock Investment Agent CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze a single stock"
    )
    analyze_parser.add_argument("--ticker", required=True)
    analyze_parser.add_argument("--period", default="1y")
    analyze_parser.set_defaults(func=handle_analyze)

    # Rank
    rank_parser = subparsers.add_parser(
        "rank", help="Rank multiple stocks"
    )
    rank_parser.add_argument("--tickers", required=True)
    rank_parser.add_argument("--period", default="1y")
    rank_parser.set_defaults(func=handle_rank)

    # Portfolio
    portfolio_parser = subparsers.add_parser(
        "portfolio", help="Build a simulated portfolio"
    )
    portfolio_parser.add_argument("--tickers", required=True)
    portfolio_parser.add_argument("--budget", required=True, type=float)
    portfolio_parser.add_argument("--period", default="1y")
    portfolio_parser.add_argument("--max-weight", default=0.40, type=float)
    portfolio_parser.set_defaults(func=handle_portfolio)

    # Backtest
    backtest_parser = subparsers.add_parser(
        "backtest", help="Backtest a ranked portfolio"
    )
    backtest_parser.add_argument("--tickers", required=True)
    backtest_parser.add_argument("--capital", default=10000.0, type=float)
    backtest_parser.add_argument("--period", default="1y")
    backtest_parser.set_defaults(func=handle_backtest)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as exc:
        output_json({"error": str(exc)})
        sys.exit(1)


if __name__ == "__main__":
    main()
