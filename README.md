# Autoresearch Trading

Generic autoresearch framework for testing trading strategies on any scrip with
local OHLCV CSV data.

The default strategy template is Open Range Breakout, but the project is not
tied to any specific symbol. Configure your instrument and data files in
`project_config.py`.

## Quick Start

1. Put your CSV files in `data/`.
2. Edit `project_config.py`.
3. Edit `strategy.py` if needed.
4. Run:

```powershell
python backtest.py
```

For an autoresearch loop:

```powershell
python autoresearch.py
```

## Files

| File | Purpose |
| --- | --- |
| `project_config.py` | Symbol, CSV paths, dates, capital, goals, session timings |
| `strategy.py` | Editable strategy parameters |
| `engine.py` | Generic data loading, indicators, ORB backtest, metrics |
| `backtest.py` | Runs one backtest |
| `autoresearch.py` | Keep/reject experiment loop |
| `exporters.py` | Saves kept strategy, README, and reusable backtesting script |
| `BACKTESTING_CHECKLIST.md` | Backtesting assumptions used by the research loop |
| `program.md` | Operating instructions for autoresearch |
| `results.tsv` | Experiment log |
| `kept_strategies/` | Separate folder for every kept strategy |

## Data Format

Default CSV schema:

```text
date,time,open,high,low,close,volume
```

Example:

```text
2026-01-01,09:15:00,100.0,101.0,99.5,100.8,123456
```

## Output

Every kept strategy is exported to:

```text
kept_strategies/<rank>_<return>_return/
```

Each kept folder contains:

```text
strategy_file/
  strategy.py
readme_file/
  README.md
backtesting_file/
  <strategy>_Backtest_<rank>.py
```

The README explains the strategy settings, project settings, and performance
metrics for that kept strategy. The backtesting file keeps a sectioned
`CONFIG` block for capital, symbol, timing, entry/exit assumptions, costs,
slippage, risk controls, and all selected strategy parameters, so it can be
backtested or optimized later.

## Backtesting Controls

`project_config.py` includes execution-realism controls used by both direct
backtests and the autoresearch keep/reject loop:

- candle timestamp convention
- signal evaluation mode: `intrabar` or `candle_close`
- entry execution mode: `trigger`, `close`, or `next_open`
- same-candle re-entry blocking
- gap-through stop handling
- separate entry, stop, target, and square-off slippage
- daily loss blocking and max trades per day
- indicator warmup/NaN trade blocking

See `BACKTESTING_CHECKLIST.md` for the full checklist.
