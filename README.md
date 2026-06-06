# Autoresearch Trading

Generic trading autoresearch framework for testing, rejecting, keeping, and
exporting intraday strategies on any scrip using local OHLCV CSV data.

The default template is Open Range Breakout, but the project is intentionally
not tied to Reliance or any one instrument. Configure the symbol, comparison
index, date range, capital, timings, goals, and CSV paths in
`project_config.py`.

## What This Project Does

- Runs one clean backtest with `python backtest.py`.
- Runs a keep/reject research loop with `python autoresearch.py`.
- Commits every experiment before testing it.
- Keeps only strategies that pass the configured goals and improve the current
  best result.
- Exports every kept strategy into a separate folder with:
  - exact strategy file
  - full readable README
  - reusable backtesting file with a sectioned `CONFIG` block
- Applies stricter backtesting controls for execution timing, slippage,
  warmup, same-candle behavior, re-entry, daily risk, and goal validation.

## Project Structure

```text
Autoresearch_Trading/
  README.md
  pyproject.toml
  project_config.py
  strategy.py
  engine.py
  backtest.py
  autoresearch.py
  exporters.py
  results.tsv
  data/
    README.md
  docs/
    WORKFLOW.md
    BACKTESTING_CHECKLIST.md
  kept_strategies/
    README.md
    <rank>_<return>_return/
      strategy_file/
        strategy.py
      readme_file/
        README.md
      backtesting_file/
        <strategy>_Backtest_<rank>.py
```

## File Meaning

| File / Folder | Purpose |
| --- | --- |
| `project_config.py` | Project-level settings: symbol, compare symbol, CSV paths, dates, capital, goals, session times, execution assumptions, costs, slippage, and risk limits. |
| `strategy.py` | Strategy-level parameters changed by manual tests and the autoresearch loop. |
| `engine.py` | Data loading, indicator calculation, ORB signal logic, trade simulation, costs, drawdown, and metrics. |
| `backtest.py` | Runs one strategy backtest using current `project_config.py` and `strategy.py`. |
| `autoresearch.py` | Keep/reject experiment runner. Edits strategy parameters, commits tests, logs results, exports kept strategies, resets rejected commits. |
| `exporters.py` | Creates the three kept-strategy artifact folders and generated backtesting script. |
| `results.tsv` | Experiment log with commit, return, drawdown, keep/discard status, and description. |
| `data/` | Local OHLCV CSV files. |
| `docs/WORKFLOW.md` | Detailed operating workflow. |
| `docs/BACKTESTING_CHECKLIST.md` | Backtesting safety checklist used while evaluating strategies. |
| `kept_strategies/` | Final selected strategy artifacts. |

## Quick Start

1. Put CSV files in `data/`.
2. Edit `project_config.py`.
3. Edit `strategy.py` if testing manually.
4. Run a single backtest:

```powershell
python backtest.py
```

5. Run the autoresearch loop:

```powershell
python autoresearch.py
```

## CSV Format

Default expected columns:

```text
date,time,open,high,low,close,volume
```

Column names can be changed in `project_config.py`:

```python
date_column = "date"
time_column = "time"
open_column = "open"
high_column = "high"
low_column = "low"
close_column = "close"
volume_column = "volume"
```

Example config:

```python
symbol = "RELIANCE"
compare_symbol = "NIFTY"
symbol_csv = "data/RELIANCE_NSE_5m.csv"
compare_csv = "data/NIFTY_NSE_INDEX_5m.csv"
```

## Core Backtest Rules

These rules are controlled in `project_config.py` and used by both direct
backtests and the autoresearch keep/reject loop.

| Area | Setting |
| --- | --- |
| Candle timing | `candle_timestamp = "open"` or `"close"` documents source timestamp convention. |
| Signal evaluation | `signal_evaluation_mode = "intrabar"` checks high/low breakout; `"candle_close"` checks confirmed close only. |
| Entry execution | `entry_execution_mode = "trigger"`, `"close"`, or `"next_open"`. |
| Gap handling | Breakout entries use worse open if price gaps beyond trigger. |
| Stop handling | Gap-through stop can use worse open instead of exact stop. |
| Same-candle behavior | Stop is checked before target; same-candle re-entry can be blocked. |
| Re-entry | `max_reentries` caps entries per direction per day; only one open position is supported. |
| Costs | `cost_bps` applies all-in turnover cost. |
| Slippage | Separate entry, stop, target, and square-off slippage bps are available. |
| Warmup | Active indicators do not pass on NaN/warmup values unless explicitly allowed. |
| Daily risk | Optional max trades per day and daily loss blocking are supported. |
| Goal validation | Minimum return, maximum drawdown, and optional minimum trade count are checked. |

## Indicator Definitions

The engine calculates only the indicators needed by the current strategy shape:

- ATR 14 using Wilder smoothing.
- DMI/ADX 14 using Wilder smoothing.
- EMA 20 and EMA 50.
- Volume ratio as `volume / SMA20(volume)`.
- Previous day high and low.
- Relative strength versus comparison symbol when configured.
- Regression slope over 12 candles.

### Regression Slope Note

The slope is normalized so it is comparable across price levels:

```text
slope12 = linear_regression_slope(close, 12) / mean(close, 12) * 100
```

This matters. A raw rupee-point slope can look larger on high-priced stocks and
smaller on low-priced stocks even when the percentage trend is similar. Any
future slope filter should clearly state whether it uses normalized percentage
slope or raw price slope. This project uses normalized percentage slope.

## Kept Strategy Output

Every kept strategy is exported like this:

```text
kept_strategies/001_18.2500_return/
  strategy_file/
    strategy.py
  readme_file/
    README.md
  backtesting_file/
    Open_Range_Breakout_Backtest_001.py
```

Use `strategy_file/strategy.py` when you want the exact compact strategy config.
Use `readme_file/README.md` when you want the full settings and results summary.
Use `backtesting_file/*.py` when you want a reusable script with all settings in
one sectioned `CONFIG` block for later backtesting or optimization.

## Keep / Reject Logic

`autoresearch.py` follows this loop:

1. Build a candidate parameter set.
2. Write it into `strategy.py`.
3. Commit the experiment.
4. Run the backtest.
5. Append result to `results.tsv`.
6. Keep only if:
   - return is at least `min_return_pct`
   - drawdown is at most `max_drawdown_pct`
   - trade count is at least `min_trades_for_goal`
   - result improves the current best kept strategy
7. Export kept artifacts.
8. Reset rejected experiment commits.

## Important Guardrails

- Do not change `engine.py` while comparing strategies unless you intentionally
  want to change the backtest rules.
- Do not compare results from two different execution modes as if they are the
  same strategy. `trigger`, `close`, and `next_open` can produce very different
  trade counts and returns.
- Do not trust high return with very few trades. Set `min_trades_for_goal` when
  you want to reject low-sample results.
- Use realistic costs and slippage before trusting any result.
- Check random trades manually before moving a strategy toward live trading.
- Prefer train/test or walk-forward validation when optimizing many parameters.

## Current Defaults

The repository ships with safe generic defaults, not a finished symbol-specific
strategy. Before running serious research, update:

- `symbol`
- `compare_symbol`
- `symbol_csv`
- `compare_csv`
- `start_date`
- `end_date`
- `allocation`
- `min_return_pct`
- `max_drawdown_pct`
- `opening_range_minutes`
- execution mode and slippage assumptions

For detailed workflow steps, see `docs/WORKFLOW.md`. For the full backtesting
checklist, see `docs/BACKTESTING_CHECKLIST.md`.
