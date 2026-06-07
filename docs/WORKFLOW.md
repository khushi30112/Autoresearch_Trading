# Autoresearch Trading Workflow

This document is the operating runbook. The root `README.md` explains the
project structure and assumptions.

## 1. Configure A New Scrip

Edit `project_config.py`:

- `symbol`
- `compare_symbol`
- `symbol_csv`
- `compare_csv`
- `start_date`
- `end_date`
- `timeframe`
- `allocation`
- `min_return_pct`
- `max_drawdown_pct`
- session and ORB timings
- execution mode, costs, slippage, and risk controls

Put CSV files under `data/` by default.

## 2. Confirm Data Shape

Default columns:

```text
date,time,open,high,low,close,volume
```

If the source uses different names, update the CSV schema fields in
`project_config.py`.

Before trusting a run, check:

- date and time parse correctly
- candles are sorted
- no duplicate timestamps
- no impossible OHLC values
- enough warmup candles exist for active indicators
- comparison symbol timestamps align with symbol timestamps

## 3. Run One Backtest

Use the current `strategy.py`:

```powershell
python backtest.py
```

Review:

- return
- max drawdown
- number of trades
- win rate
- profit factor
- goal pass/fail
- printed strategy config

## 4. Run Autoresearch

```powershell
python autoresearch.py
```

The loop:

1. Generates a candidate.
2. Updates `strategy.py`.
3. Commits the experiment.
4. Runs the backtest.
5. Logs to `results.tsv`.
6. Keeps only goal-passing improvements.
7. Exports kept strategy artifacts.
8. Resets discarded commits.

## 5. Read Results

Open `results.tsv`.

Columns:

```text
commit, return_pct, max_drawdown_pct, status, description
```

`keep` means the strategy passed goals and improved the best known result.
`discard` means it failed goals or did not improve the best kept result.

## 6. Use A Kept Strategy

Each kept strategy has:

```text
Strategy_<rank>.py
README_<rank>.md
<strategy>_Backtest_<rank>.py
```

Use the compact strategy file for this project. Use the generated backtesting
file when you want all settings in one sectioned script for later replay,
optimization, and report generation.

In generated backtesting files, edit the top `CONFIG` block only. Values such
as `SYMBOLS`, `SYMBOL_CSV`, `COMPARE_CSV`, `BACKTEST_START_DATE`,
`BACKTEST_END_DATE`, execution mode, costs, goals, and output settings are read
from that block at runtime.

## 7. Change Strategy Ideas Safely

Add candidate ideas in `generate_candidates()` inside `autoresearch.py`.

Recommended experiment areas:

- breakout buffer
- ADX/DMI filters
- ATR percent filters
- volume ratio filters
- EMA trend filter
- normalized regression slope filters
- relative strength filter
- stop mode
- target R multiple
- trailing stop mode
- max re-entries
- daily trade limit
- slippage and cost stress tests

## 8. Do Not Mix Backtest Rules Accidentally

Changing these can make old and new results incomparable:

- `entry_execution_mode`
- `signal_evaluation_mode`
- `block_same_candle_reentry`
- slippage and cost settings
- stop/target same-candle policy
- indicator warmup behavior
- slope calculation method

If any of these change, treat the run as a new research regime.
