# Autoresearch Trading Workflow

This project is a generic autoresearch framework for trading strategies.

## Configure A New Scrip

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
- session timings

Place CSV files under `data/` by default.

Expected CSV columns by default:

```text
date,time,open,high,low,close,volume
```

Column names can be changed in `project_config.py`.

## Strategy Experiments

Edit `strategy.py` for manual experiments.

Run one backtest:

```powershell
python backtest.py
```

Run the autoresearch loop:

```powershell
python autoresearch.py
```

## Keep / Reject Rules

The runner:

1. Edits `strategy.py`.
2. Commits the experiment.
3. Runs the backtest.
4. Logs the result in `results.tsv`.
5. Keeps the commit only if it passes goals and improves the current best.
6. Exports every kept strategy into `kept_strategies/<rank>/`.
7. Resets discarded strategies.

Every kept strategy folder contains:

- `strategy.py`
- `README.md` with full settings and metrics

## Important

Do not change `engine.py` while comparing experiments unless you intentionally
want to change the backtest rules.
