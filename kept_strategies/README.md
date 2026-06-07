# Kept Strategies

This folder contains only selected strategies that passed the configured goals
and improved the current best result during autoresearch.

Each kept strategy is saved as one folder with direct files:

```text
<rank>_<return>_return/
  Strategy_<rank>.py
  README_<rank>.md
  <strategy>_Backtest_<rank>.py
```

## Which File To Use

| File | Use |
| --- | --- |
| `Strategy_<rank>.py` | Exact compact `strategy.py` from the kept commit. Use this inside `Autoresearch_Trading`. |
| `README_<rank>.md` | Human-readable summary of result, capital, symbol, timings, indicators, execution assumptions, costs, risk controls, and parameters. |
| `<strategy>_Backtest_<rank>.py` | Report-generating backtesting adapter with a sectioned `CONFIG` block for later replay or optimization. |

## Important

Do not compare kept strategies unless they were produced with the same
`project_config.py` execution assumptions. Entry mode, signal mode, slippage,
same-candle rules, warmup handling, and slope definition can materially change
results.
