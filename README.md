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
strategy.py
README.md
```

The README explains the strategy settings, project settings, and performance
metrics for that kept strategy.
