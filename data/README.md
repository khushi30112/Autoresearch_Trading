# Data Folder

Place local OHLCV CSV files here.

Default expected columns:

```text
date,time,open,high,low,close,volume
```

Example `project_config.py` settings:

```python
symbol = "RELIANCE"
compare_symbol = "NIFTY"
symbol_csv = "data/RELIANCE_NSE_5m.csv"
compare_csv = "data/NIFTY_NSE_INDEX_5m.csv"
```

Before running serious research, verify:

- timestamps parse correctly
- candle interval matches `timeframe`
- no duplicate candles
- no missing candles in active sessions
- OHLC values are valid: `high >= open/close/low` and `low <= open/close/high`
- enough warmup candles exist before the tested range
- comparison data aligns with symbol data timestamps

If your CSV uses different column names, update the column mapping fields in
`project_config.py`.
