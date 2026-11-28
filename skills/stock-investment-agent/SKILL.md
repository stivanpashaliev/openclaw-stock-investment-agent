---
name: stock-investment-agent
description: Analyze stocks using real market data, calculate financial risk and return metrics, rank a stock universe, construct a simulated investment portfolio from a user budget, and backtest portfolio performance. Use when users request stock analysis, comparisons, rankings, portfolio allocation, or historical performance simulations.
---

# Stock Investment Agent

## Overview

This Skill provides a workflow for using the Stock Investment Agent Python engine.
It retrieves market data, calculates deterministic metrics, ranks stocks,
constructs simulated portfolios, and evaluates historical performance.

Python is responsible for numerical calculations. The AI interprets the returned
results, explains trade-offs, and communicates limitations. Never invent
financial data or claim a tool ran when it did not.

## Capabilities

- `analyze`: analyze one stock's historical performance.
- `rank`: compare and rank multiple stocks.
- `portfolio`: create a budget-based simulated portfolio.
- `backtest`: simulate portfolio performance on historical price data.

## Project Setup

Project root:

`~/projects/stock-investment-agent`

Use the project's virtual environment Python:

`./.venv/bin/python`

Run commands from the project root and set `PYTHONPATH=src`.

## Workflow

### 1. Understand the user's request

Identify:
- Stock ticker symbols
- Analysis period (default: `1y`)
- Budget, if portfolio construction is requested
- Whether the user wants analysis, ranking, portfolio construction, backtesting, or a combination

Ask only for essential missing information. Do not silently assume a budget.

### 2. Analyze a single stock

Use:

`PYTHONPATH=src ./.venv/bin/python -m stock_agent.cli analyze TICKER --period 1y`

Replace `TICKER` with the requested symbol and period with the requested supported period.

Explain the returned total return, annualized volatility, and maximum drawdown. Distinguish historical performance from future expectations.

### 3. Rank multiple stocks

Use:

`PYTHONPATH=src ./.venv/bin/python -m stock_agent.cli rank --tickers AAPL,MSFT,NVDA,GOOGL,AMZN --period 1y`

Replace the example tickers with the user's list.

The ranking uses the project's weighted scoring methodology:
- Return: 50%
- Volatility: 25% (lower is better)
- Maximum drawdown: 25% (smaller drawdown is better)

Scores are normalized relative to the selected stock universe. A score of 100
does not mean a stock is universally best; it means it scores best within
the current comparison set.

### 4. Build a simulated portfolio

Use:

`PYTHONPATH=src ./.venv/bin/python -m stock_agent.cli portfolio --tickers AAPL,MSFT,NVDA,GOOGL,AMZN --budget 10000 --period 1y`

Replace tickers, budget, and period with the user's request.

Explain:
- Each holding and its ticker
- Score and portfolio weight
- Number of whole shares
- Amount invested
- Remaining cash

The Portfolio Builder uses ranking scores, enforces position-size limits,
and buys whole shares only. Stocks with zero scores may be excluded.
Cash can remain uninvested due to allocation limits or whole-share rounding.

This is a simulation, not a trade order.

### 5. Run a backtest

Use:

`PYTHONPATH=src ./.venv/bin/python -m stock_agent.cli backtest --tickers AAPL,MSFT,NVDA,GOOGL,AMZN --capital 10000 --period 1y`

Replace the example tickers, capital, and period as needed.

Explain the returned:
- Total return
- Annualized return
- Annualized volatility
- Maximum drawdown
- Sharpe ratio
- Portfolio value over time

Important methodological limitation: the current backtesting workflow derives
weights using rankings from the same historical period being simulated. This
introduces look-ahead bias. Results are illustrative and must not be presented
as proof of future profitability or as a valid predictive backtest. A
walk-forward backtest is a future improvement.

### 6. Combined analysis workflow

When a user asks for a full investment analysis:

1. Analyze or rank the requested stocks.
2. If a budget is provided, build a simulated portfolio.
3. If historical evaluation is requested, run a backtest.
4. Summarize the results using the actual tool outputs.
5. Explain the methodology, risks, assumptions, and limitations.

Do not run unnecessary operations. If a user only asks for ranking, do not
automatically build a portfolio or backtest unless it is useful or requested.

## Financial Safety and Accuracy

- Never fabricate prices, returns, scores, holdings, or backtest results.
- Use actual tool output for all numerical claims.
- If a command fails or data is unavailable, state that clearly.
- Historical performance is not a guarantee of future performance.
- This project provides analysis and simulation only; it does not execute trades.
- Explain that the stock scoring system is a project methodology, not a
  universally accepted investment standard.
- Avoid claiming certainty or guaranteed returns.
- Clearly identify the backtesting look-ahead-bias limitation.
- Do not expose API keys, credentials, or environment secrets.
- Do not execute unrelated shell commands or modify project files during
  analysis unless the user explicitly requests development work.

## Response Format

When presenting an investment analysis, prefer this structure:

1. **Executive summary**
2. **Ranking or portfolio table**
3. **Key metrics**
4. **Why the results look this way**
5. **Risks and limitations**
6. **Methodology and data period**

Be concise, transparent, and understandable to a non-expert.
