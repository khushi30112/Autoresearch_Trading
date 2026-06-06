# Data Folder

Put OHLCV CSV files here.

Default expected columns:

```text
date,time,open,high,low,close,volume
```

Then update `project_config.py`:

```python
symbol = "RELIANCE"
symbol_csv = "data/RELIANCE_NSE_5m.csv"
compare_symbol = "NIFTY"
compare_csv = "data/NIFTY_NSE_INDEX_5m.csv"
```
