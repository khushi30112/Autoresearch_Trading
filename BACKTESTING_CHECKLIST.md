# Effective Backtesting Checklist

Use this before trusting any strategy result from the autoresearch loop.

## Must-Fix Backtest Rules

- Define candle timestamp clearly: open-time candle or close-time candle.
- Prefer entry on next candle open for conservative realistic backtests.
- Avoid running-candle entry on 5m OHLC unless using tick or 1m data.
- If entry is on candle close, use only confirmed candle data.
- Do not use future candle high, low, or close for entry decisions.

## Entry Execution

- `close` means enter at signal candle close.
- `next_open` means enter at next candle open.
- `trigger` models intrabar breakout and should be used only when that assumption is intentional.
- Add realistic slippage on breakout entries.
- If price gaps beyond trigger, use the worse available price, not the ideal trigger.

## Stop Loss And Target

- Stop loss and target are checked with candle high/low after entry is valid.
- If stop and target hit in the same candle, use a conservative rule or lower-timeframe data.
- Gap-through stop should exit at the worse available price, not exact stop.
- Target fill should not always assume a perfect fill; use target slippage when needed.

## Re-Entry Rules

- `max_open_positions = 1` means only one open position at a time.
- Use separate daily trade limits when needed.
- Block same-candle exit and re-entry unless lower-timeframe data confirms the sequence.
- For ORB, repeated re-entry at the same trigger should be intentional and capped.

## Costs And Slippage

- Include brokerage, STT, exchange charges, GST, SEBI charges, stamp duty, or an equivalent all-in cost estimate.
- Add separate slippage for entry, stop, target, and square-off.
- Include bid-ask spread for live realism.

## Data Quality

- Check missing candles, duplicate candles, wrong timestamps, bad OHLC, and wrong volume.
- Ensure holidays and half-days are handled.
- Use enough warmup candles before backtest start.
- Active indicators must not trade on NaN or warmup values.

## Portfolio Risk

- Add a daily max-loss or kill switch where needed.
- Block new trades after the daily loss limit.
- Calculate risk using realized plus open unrealized PnL where possible.
- Limit max trades per day and max loss per trade.

## Optimization Safety

- Do not over-optimize too many parameters.
- Use train/test or walk-forward testing.
- Check results across multiple symbols and periods.
- Reject strategies with very few trades.
- Compare results before and after costs/slippage.

## Final Pre-Live Check

- Backtest result should survive realistic slippage and full charges.
- Check random trade dates manually.
- Verify entry, stop, target, and square-off timestamps.
- Run paper/live simulation before real capital.
- Never deploy a strategy that only works with perfect fills.
