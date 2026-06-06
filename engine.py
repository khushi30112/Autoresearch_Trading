"""
Generic trading backtest engine for autoresearch.

The default strategy shape is Open Range Breakout, but symbol, data files,
dates, capital, session timings, and goals are configurable in project_config.py.
"""

from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from project_config import CONFIG, ProjectConfig


def _load_csv(path: Path, cfg: ProjectConfig) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path)
    required = {
        cfg.date_column,
        cfg.time_column,
        cfg.open_column,
        cfg.high_column,
        cfg.low_column,
        cfg.close_column,
        cfg.volume_column,
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{path.name} missing columns: {sorted(missing)}")

    df = df.rename(
        columns={
            cfg.date_column: "date",
            cfg.time_column: "time",
            cfg.open_column: "open",
            cfg.high_column: "high",
            cfg.low_column: "low",
            cfg.close_column: "close",
            cfg.volume_column: "volume",
        }
    )
    df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
    df["date"] = pd.to_datetime(df["date"]).dt.date
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["datetime", "open", "high", "low", "close"])
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.end_date) + pd.Timedelta(days=1)
    df = df[(df["datetime"] >= start) & (df["datetime"] < end)]
    return df.sort_values("datetime").reset_index(drop=True)


def _wilder_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = _wilder_ema(tr, 14)
    df["atr_pct"] = df["atr14"] / df["close"] * 100

    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_di = 100 * _wilder_ema(pd.Series(plus_dm, index=df.index), 14) / df["atr14"]
    minus_di = 100 * _wilder_ema(pd.Series(minus_dm, index=df.index), 14) / df["atr14"]
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df["plus_di14"] = plus_di
    df["minus_di14"] = minus_di
    df["adx14"] = _wilder_ema(dx, 14)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["vol_sma20"] = df["volume"].rolling(20, min_periods=1).mean()
    df["volume_ratio"] = df["volume"] / df["vol_sma20"].replace(0, np.nan)

    x = np.arange(12, dtype=float)
    x = x - x.mean()

    def slope(values: np.ndarray) -> float:
        y = values.astype(float)
        if np.isnan(y).any() or y.mean() == 0:
            return np.nan
        return float((x @ (y - y.mean())) / (x @ x) / y.mean() * 100)

    df["slope12"] = df["close"].rolling(12).apply(slope, raw=True)

    daily = df.groupby("date").agg(day_high=("high", "max"), day_low=("low", "min"))
    daily["prev_day_high"] = daily["day_high"].shift(1)
    daily["prev_day_low"] = daily["day_low"].shift(1)
    df = df.merge(daily[["prev_day_high", "prev_day_low"]], left_on="date", right_index=True, how="left")
    return df


def _add_compare_features(symbol_df: pd.DataFrame, compare_df: pd.DataFrame | None) -> pd.DataFrame:
    out = symbol_df.copy()
    if compare_df is None or compare_df.empty:
        out["compare_ret_intraday"] = np.nan
        out["symbol_ret_intraday"] = out["close"] / out.groupby("date")["open"].transform("first") - 1
        out["rel_strength"] = np.nan
        return out

    cmp_df = compare_df[["datetime", "open", "close"]].rename(columns={"open": "compare_open", "close": "compare_close"})
    out = out.merge(cmp_df, on="datetime", how="left")
    out["compare_ret_intraday"] = out["compare_close"] / out.groupby("date")["compare_open"].transform("first") - 1
    out["symbol_ret_intraday"] = out["close"] / out.groupby("date")["open"].transform("first") - 1
    out["rel_strength"] = (out["symbol_ret_intraday"] - out["compare_ret_intraday"]) * 100
    return out


@lru_cache(maxsize=1)
def load_market_data() -> pd.DataFrame:
    symbol_df = _add_indicators(_load_csv(CONFIG.symbol_path(), CONFIG))
    compare_path = CONFIG.compare_path()
    compare_df = _load_csv(compare_path, CONFIG) if compare_path else None
    df = _add_compare_features(symbol_df, compare_df)
    if df.empty:
        raise ValueError("No symbol data available for configured date range.")
    return df


def _opening_range(day: pd.DataFrame) -> tuple[float, float] | None:
    start = pd.Timestamp(CONFIG.session_start).time()
    end_dt = pd.Timestamp(CONFIG.session_start) + pd.Timedelta(minutes=CONFIG.opening_range_minutes)
    end = end_dt.time()
    opening = day[(pd.to_datetime(day["time"]).dt.time >= start) & (pd.to_datetime(day["time"]).dt.time < end)]
    if opening.empty:
        return None
    return float(opening["high"].max()), float(opening["low"].min())


def _allowed(row: pd.Series, direction: str, strategy: Any, day_open: float) -> bool:
    if strategy.avoid_open_beyond_prev_day:
        prev_high = row.get("prev_day_high")
        prev_low = row.get("prev_day_low")
        if pd.notna(prev_high) and day_open > prev_high:
            return False
        if pd.notna(prev_low) and day_open < prev_low:
            return False
    if pd.notna(row.get("adx14")) and row["adx14"] < strategy.adx_min:
        return False
    if pd.notna(row.get("atr_pct")):
        if row["atr_pct"] < strategy.atr_pct_min or row["atr_pct"] > strategy.atr_pct_max:
            return False
    if pd.notna(row.get("volume_ratio")) and row["volume_ratio"] < strategy.volume_ratio_min:
        return False

    slope = row.get("slope12")
    rel = row.get("rel_strength")
    if direction == "long":
        if strategy.use_dmi and row.get("plus_di14", 0) <= row.get("minus_di14", 0):
            return False
        if pd.notna(slope) and slope < strategy.long_slope_min:
            return False
        if pd.notna(rel) and rel < strategy.long_rel_strength_min:
            return False
        if strategy.ema_filter and row["close"] < row["ema20"]:
            return False
    else:
        if strategy.use_dmi and row.get("minus_di14", 0) <= row.get("plus_di14", 0):
            return False
        if pd.notna(slope) and slope > -strategy.short_slope_min:
            return False
        if pd.notna(rel) and rel > -strategy.short_rel_strength_min:
            return False
        if strategy.ema_filter and row["close"] > row["ema20"]:
            return False
    return True


def _initial_stop(direction: str, entry: float, orb_high: float, orb_low: float, row: pd.Series, strategy: Any) -> float:
    if strategy.stop_mode == "atr":
        atr = row["atr14"] if pd.notna(row.get("atr14")) else entry * strategy.stop_loss_pct / 100
        distance = max(strategy.atr_stop_mult * atr, entry * strategy.min_stop_pct / 100)
        return entry - distance if direction == "long" else entry + distance
    if strategy.stop_mode == "orb":
        return orb_low if direction == "long" else orb_high
    distance = entry * strategy.stop_loss_pct / 100
    return entry - distance if direction == "long" else entry + distance


def _target(direction: str, entry: float, stop: float, strategy: Any) -> float | None:
    if strategy.target_rr <= 0:
        return None
    risk = abs(entry - stop)
    return entry + strategy.target_rr * risk if direction == "long" else entry - strategy.target_rr * risk


def _trail(direction: str, stop: float, row: pd.Series, strategy: Any) -> float:
    if strategy.trailing_mode == "none":
        return stop
    if strategy.trailing_mode == "atr":
        atr = row["atr14"] if pd.notna(row.get("atr14")) else row["close"] * strategy.stop_loss_pct / 100
        candidate = row["close"] - strategy.atr_trail_mult * atr if direction == "long" else row["close"] + strategy.atr_trail_mult * atr
    else:
        distance = row["close"] * strategy.trailing_pct / 100
        candidate = row["close"] - distance if direction == "long" else row["close"] + distance
    return max(stop, candidate) if direction == "long" else min(stop, candidate)


def run_backtest(strategy: Any) -> dict[str, Any]:
    if CONFIG.max_open_positions != 1:
        raise ValueError("This engine currently supports max_open_positions = 1.")
    if strategy.max_reentries < 1:
        raise ValueError("max_reentries must be >= 1")

    df = load_market_data()
    trades: list[dict[str, Any]] = []
    equity = CONFIG.allocation
    equity_curve = [equity]

    breakout_time = pd.Timestamp(CONFIG.breakout_start).time()
    square_off_time = pd.Timestamp(CONFIG.square_off_time).time()

    for trade_date, day in df.groupby("date", sort=True):
        day = day.reset_index(drop=True)
        orb = _opening_range(day)
        if orb is None:
            continue
        orb_high, orb_low = orb
        day_open = float(day.loc[0, "open"])
        long_entries = 0
        short_entries = 0
        position: dict[str, Any] | None = None

        for _, row in day.iterrows():
            row_time = pd.Timestamp(row["time"]).time()
            if row_time < breakout_time:
                continue

            if position is not None:
                direction = position["direction"]
                position["stop"] = _trail(direction, position["stop"], row, strategy)
                stop = position["stop"]
                target = position["target"]
                exit_price = None
                exit_reason = None

                if direction == "long":
                    if row["low"] <= stop:
                        exit_price = stop
                        exit_reason = "stop"
                    elif target is not None and row["high"] >= target:
                        exit_price = target
                        exit_reason = "target"
                else:
                    if row["high"] >= stop:
                        exit_price = stop
                        exit_reason = "stop"
                    elif target is not None and row["low"] <= target:
                        exit_price = target
                        exit_reason = "target"

                if row_time >= square_off_time and exit_price is None:
                    exit_price = float(row["close"])
                    exit_reason = "squareoff"

                if exit_price is not None:
                    qty = position["qty"]
                    gross = (exit_price - position["entry_price"]) * qty
                    if direction == "short":
                        gross = -gross
                    costs = (position["entry_price"] + exit_price) * qty * CONFIG.cost_bps / 10000
                    pnl = gross - costs
                    equity += pnl
                    equity_curve.append(equity)
                    trades.append(
                        {
                            "date": str(trade_date),
                            "direction": direction,
                            "entry_time": position["entry_time"],
                            "exit_time": row["time"],
                            "entry_price": position["entry_price"],
                            "exit_price": exit_price,
                            "qty": qty,
                            "pnl": pnl,
                            "exit_reason": exit_reason,
                        }
                    )
                    position = None

            if position is not None or row_time >= square_off_time:
                continue

            atr = row["atr14"] if pd.notna(row.get("atr14")) else 0.0
            buffer_abs = max(strategy.breakout_buffer_pct / 100 * row["close"], strategy.breakout_atr_mult * atr)
            long_trigger = orb_high + buffer_abs
            short_trigger = orb_low - buffer_abs

            if CONFIG.allow_long and long_entries < strategy.max_reentries and row["high"] > long_trigger:
                if _allowed(row, "long", strategy, day_open):
                    entry = long_trigger if strategy.entry_price == "trigger" else float(row["close"])
                    qty = int(CONFIG.allocation // entry)
                    stop = _initial_stop("long", entry, orb_high, orb_low, row, strategy)
                    position = {
                        "direction": "long",
                        "entry_time": row["time"],
                        "entry_price": entry,
                        "qty": qty,
                        "stop": stop,
                        "target": _target("long", entry, stop, strategy),
                    }
                    long_entries += 1
                    continue

            if CONFIG.allow_short and short_entries < strategy.max_reentries and row["low"] < short_trigger:
                if _allowed(row, "short", strategy, day_open):
                    entry = short_trigger if strategy.entry_price == "trigger" else float(row["close"])
                    qty = int(CONFIG.allocation // entry)
                    stop = _initial_stop("short", entry, orb_high, orb_low, row, strategy)
                    position = {
                        "direction": "short",
                        "entry_time": row["time"],
                        "entry_price": entry,
                        "qty": qty,
                        "stop": stop,
                        "target": _target("short", entry, stop, strategy),
                    }
                    short_entries += 1

        if position is not None:
            row = day.iloc[-1]
            exit_price = float(row["close"])
            qty = position["qty"]
            gross = (exit_price - position["entry_price"]) * qty
            if position["direction"] == "short":
                gross = -gross
            costs = (position["entry_price"] + exit_price) * qty * CONFIG.cost_bps / 10000
            pnl = gross - costs
            equity += pnl
            equity_curve.append(equity)
            trades.append(
                {
                    "date": str(trade_date),
                    "direction": position["direction"],
                    "entry_time": position["entry_time"],
                    "exit_time": row["time"],
                    "entry_price": position["entry_price"],
                    "exit_price": exit_price,
                    "qty": qty,
                    "pnl": pnl,
                    "exit_reason": "eod",
                }
            )

    equity_series = pd.Series(equity_curve, dtype=float)
    drawdown = (equity_series.cummax() - equity_series) / CONFIG.allocation * 100
    trades_df = pd.DataFrame(trades)
    total_pnl = float(trades_df["pnl"].sum()) if not trades_df.empty else 0.0
    wins = int((trades_df["pnl"] > 0).sum()) if not trades_df.empty else 0
    losses = int((trades_df["pnl"] <= 0).sum()) if not trades_df.empty else 0
    gross_profit = float(trades_df.loc[trades_df["pnl"] > 0, "pnl"].sum()) if not trades_df.empty else 0.0
    gross_loss = abs(float(trades_df.loc[trades_df["pnl"] <= 0, "pnl"].sum())) if not trades_df.empty else 0.0

    first = df.iloc[0]
    last = df.iloc[-1]
    symbol_buy_hold = (last["close"] / first["open"] - 1) * 100

    return_pct = total_pnl / CONFIG.allocation * 100
    max_dd = float(drawdown.max()) if len(drawdown) else 0.0
    return {
        "return_pct": return_pct,
        "max_drawdown_pct": max_dd,
        "net_pnl": total_pnl,
        "final_equity": CONFIG.allocation + total_pnl,
        "num_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate_pct": wins / len(trades) * 100 if trades else 0.0,
        "profit_factor": gross_profit / gross_loss if gross_loss else (np.inf if gross_profit else 0.0),
        "symbol_buy_hold_pct": float(symbol_buy_hold),
        "goal_pass": return_pct >= CONFIG.min_return_pct and max_dd <= CONFIG.max_drawdown_pct,
        "project": asdict(CONFIG),
        "config": asdict(strategy),
        "trades": trades,
    }
