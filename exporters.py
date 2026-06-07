"""
Kept-strategy artifact exporters.

Each accepted strategy gets one clearly named folder containing three direct
files:
- Strategy_<rank>.py: exact compact strategy config
- README_<rank>.md: readable settings and result summary
- <strategy>_Backtest_<rank>.py: reusable report-generating backtest script
"""

from __future__ import annotations

import subprocess
from dataclasses import asdict
from pathlib import Path
from pprint import pformat

from project_config import CONFIG, ROOT
from strategy import StrategyConfig


KEPT_DIR = ROOT / "kept_strategies"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in value).strip("_")


def _strategy_config_literal(values: dict[str, object]) -> str:
    comments = {
        "entry_price": "Strategy entry preference; project entry mode controls final fill model.",
        "breakout_buffer_pct": "Extra breakout buffer as percent of close.",
        "breakout_atr_mult": "Extra breakout buffer as ATR multiple.",
        "max_reentries": "Max entries per direction per day.",
        "avoid_open_beyond_prev_day": "Skip day if open is outside previous day range.",
        "adx_min": "Minimum ADX14; 0 disables.",
        "atr_pct_min": "Minimum ATR14 percent.",
        "atr_pct_max": "Maximum ATR14 percent.",
        "volume_ratio_min": "Minimum volume/SMA20 volume ratio.",
        "use_dmi": "Require directional DMI alignment.",
        "ema_filter": "Require close/EMA20 trend alignment.",
        "long_slope_min": "Minimum normalized slope12 for longs.",
        "short_slope_min": "Minimum bearish slope12 magnitude for shorts.",
        "long_rel_strength_min": "Minimum relative strength for longs.",
        "short_rel_strength_min": "Minimum relative weakness for shorts.",
        "stop_mode": "Initial stop mode: orb, atr, or percent.",
        "stop_loss_pct": "Percent stop when stop_mode is percent.",
        "min_stop_pct": "Minimum ATR stop distance percent.",
        "atr_stop_mult": "ATR14 multiple for ATR stop.",
        "target_rr": "Reward/risk target; <=0 disables target.",
        "trailing_mode": "Trailing mode: none, atr, or percent.",
        "atr_trail_mult": "ATR14 multiple for ATR trail.",
        "trailing_pct": "Percent distance for percent trail.",
    }
    lines = ["{"]
    for key, value in values.items():
        comment = comments.get(key, "")
        suffix = f"  # {comment}" if comment else ""
        lines.append(f"    {key!r}: {value!r},{suffix}")
    lines.append("}")
    return "\n".join(lines)


def _write_root_readme() -> None:
    (KEPT_DIR / "README.md").write_text(
        """# Kept Strategies

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
"""
    )


def _readme(rank: int, commit: str, description: str, strategy: StrategyConfig, result: dict) -> str:
    project = result.get("project", asdict(CONFIG))
    settings = asdict(strategy)
    return f"""# Kept Strategy {rank:03d}

Commit: `{commit}`

Description: {description}

## Results

| Metric | Value |
| --- | ---: |
| Return | {result['return_pct']:.4f}% |
| Max drawdown | {result['max_drawdown_pct']:.4f}% |
| Net PnL | {result['net_pnl']:.2f} |
| Final equity | {result['final_equity']:.2f} |
| Trades | {result['num_trades']} |
| Wins | {result['wins']} |
| Losses | {result['losses']} |
| Win rate | {result['win_rate_pct']:.2f}% |
| Profit factor | {result['profit_factor']:.4f} |
| Symbol buy-hold | {result['symbol_buy_hold_pct']:.4f}% |

## Project Settings

| Setting | Value |
| --- | --- |
| Strategy name | {project['strategy_name']} |
| Symbol | {project['symbol']} |
| Compare symbol | {project['compare_symbol']} |
| Symbol CSV | {project['symbol_csv']} |
| Compare CSV | {project['compare_csv']} |
| Period | {project['start_date']} to {project['end_date']} |
| Time frame | {project['timeframe']} |
| Allocation | {project['allocation']} |
| Minimum return goal | {project['min_return_pct']}% |
| Maximum drawdown goal | {project['max_drawdown_pct']}% |
| Session start | {project['session_start']} |
| Opening range minutes | {project['opening_range_minutes']} |
| Breakout start | {project['breakout_start']} |
| Square-off time | {project['square_off_time']} |
| Long allowed | {project['allow_long']} |
| Short allowed | {project['allow_short']} |
| Max open positions | {project['max_open_positions']} |

## Backtesting Assumptions

| Setting | Value |
| --- | --- |
| Candle timestamp | {project['candle_timestamp']} |
| Signal evaluation mode | {project['signal_evaluation_mode']} |
| Entry execution mode | {project['entry_execution_mode']} |
| Same-candle SL/target policy | {project['same_candle_stop_target_policy']} |
| Block same-candle re-entry | {project['block_same_candle_reentry']} |
| Allow indicator NaN trades | {project['allow_indicator_nan_trades']} |
| Gap-through stop uses open | {project['gap_through_stop_uses_open']} |
| Cost bps | {project['cost_bps']} |
| Entry slippage bps | {project['entry_slippage_bps']} |
| Stop slippage bps | {project['stop_slippage_bps']} |
| Target slippage bps | {project['target_slippage_bps']} |
| Square-off slippage bps | {project['squareoff_slippage_bps']} |
| Max trades per day | {project['max_trades_per_day']} |
| Daily loss limit pct | {project['daily_loss_limit_pct']} |
| Block after daily loss | {project['block_after_daily_loss']} |
| Minimum trades for goal | {project['min_trades_for_goal']} |

## Strategy Parameters

| Parameter | Value |
| --- | --- |
""" + "".join(f"| `{key}` | `{value}` |\n" for key, value in settings.items())


def _backtesting_script(rank: int, commit: str, description: str, strategy: StrategyConfig, result: dict) -> str:
    project_config = asdict(CONFIG)
    strategy_config = asdict(strategy)
    strategy_config_literal = _strategy_config_literal(strategy_config)
    symbols = [CONFIG.symbol]
    strategy_file_name = f"{_safe_name(CONFIG.strategy_name)}_Backtest_{rank:03d}.py"
    return f'''"""
Intraday NSE Cash Breakout Backtester + Flexible Optimizer

Generated by Autoresearch_Trading for kept strategy {rank:03d}.

This file keeps the same sectioned settings style as the larger ORB backtesting
template, but delegates execution to this project's generic engine so the logic
stays identical to the research run.
"""

# ============================================================
# 1) USER PARAMETERS - CHANGE SETTINGS HERE ONLY
# ============================================================

SYMBOLS = {symbols!r}  # Active symbol list; first symbol is used by this single-symbol kept backtest.

CONFIG = {{
    # A) Run mode
    "MODE": "Backtest",  # Label for this file.
    "RUN_OPTIMIZATION": False,  # False runs one backtest; True runs OPTIMIZE_PARAMS combinations.
    "OPTIMIZATION_MODE": "single_strategy",  # Kept strategy replay/optimizer mode.

    # B) Symbols and data source
    "STRATEGY_NAME": {CONFIG.strategy_name!r},  # Report and generated file label.
    "SYMBOLS": SYMBOLS,  # Edit this and SYMBOL_CSV when replaying another script.
    "COMPARE_SYMBOL": {CONFIG.compare_symbol!r},  # Optional comparison symbol for relative strength.
    "DATA_SOURCE": "csv",  # This adapter uses local CSV files.
    "DATA_TIME_FRAME": {CONFIG.timeframe!r},  # Raw CSV timeframe label.
    "BACKTEST_TIME_FRAME": {CONFIG.timeframe!r},  # Backtest timeframe label.
    "DATA_START_DATE": {CONFIG.start_date!r},  # Data window start; changing this updates the engine config.
    "DATA_END_DATE": {CONFIG.end_date!r},  # Data window end; changing this updates the engine config.
    "BACKTEST_START_DATE": {CONFIG.start_date!r},  # Trade/backtest start date used by ProjectConfig.
    "BACKTEST_END_DATE": {CONFIG.end_date!r},  # Trade/backtest end date used by ProjectConfig.
    "SYMBOL_CSV": {CONFIG.symbol_csv!r},  # CSV path relative to project root unless absolute.
    "COMPARE_CSV": {CONFIG.compare_csv!r},  # Optional comparison CSV path.
    "DATE_COLUMN": {CONFIG.date_column!r},  # Date column in CSV.
    "TIME_COLUMN": {CONFIG.time_column!r},  # Time column in CSV.
    "OPEN_COLUMN": {CONFIG.open_column!r},  # Open price column in CSV.
    "HIGH_COLUMN": {CONFIG.high_column!r},  # High price column in CSV.
    "LOW_COLUMN": {CONFIG.low_column!r},  # Low price column in CSV.
    "CLOSE_COLUMN": {CONFIG.close_column!r},  # Close price column in CSV.
    "VOLUME_COLUMN": {CONFIG.volume_column!r},  # Volume column in CSV.

    # C) Capital, sizing, and direction
    "AMOUNT_INVESTED": {CONFIG.allocation!r},  # Fixed allocation per position/backtest.
    "INITIAL_CAPITAL": {CONFIG.allocation!r},  # Starting equity for returns and reports.
    "MAX_POSITIONS": {CONFIG.max_open_positions!r},  # Engine currently supports 1 open position.
    "DIRECTION_MODE": {"both" if CONFIG.allow_long and CONFIG.allow_short else "long" if CONFIG.allow_long else "short"!r},  # "long", "short", or "both".

    # D) Market timing
    "MARKET_OPEN": {CONFIG.session_start!r},  # Session start used for opening range.
    "OPENING_RANGE_MINUTES": {CONFIG.opening_range_minutes!r},  # Opening range length in minutes.
    "STRATEGY_START": {CONFIG.breakout_start!r},  # First time breakout signals are allowed.
    "FORCE_EXIT": {CONFIG.square_off_time!r},  # Intraday square-off time.

    # E) Candle timing and execution-price controls
    "CANDLE_TIMESTAMP": {CONFIG.candle_timestamp!r},  # Source timestamp convention: "open" or "close".
    "SIGNAL_EVALUATION_MODE": {CONFIG.signal_evaluation_mode!r},  # "candle_close" or "intrabar".
    "ENTRY_PRICE_MODE": {CONFIG.entry_execution_mode!r},  # "trigger", "close", or "next_open".
    "SAME_CANDLE_STOP_TARGET_POLICY": {CONFIG.same_candle_stop_target_policy!r},  # Same-candle exit priority.
    "BLOCK_SAME_CANDLE_REENTRY": {CONFIG.block_same_candle_reentry!r},  # Prevent reentry on the exit candle.
    "GAP_THROUGH_STOP_USES_OPEN": {CONFIG.gap_through_stop_uses_open!r},  # Use worse open on stop gaps.
    "ALLOW_INDICATOR_NAN_TRADES": {CONFIG.allow_indicator_nan_trades!r},  # Allow/deny warmup NaN trades.

    # F) Re-entry control
    "MAX_LONG_ENTRIES_PER_SYMBOL_PER_DAY": {strategy.max_reentries!r},  # Max long entries per day.
    "MAX_SHORT_ENTRIES_PER_SYMBOL_PER_DAY": {strategy.max_reentries!r},  # Max short entries per day.
    "MAX_TRADES_PER_DAY": {CONFIG.max_trades_per_day!r},  # Optional total daily trade cap.

    # G) Costs and slippage
    "COST_BPS": {CONFIG.cost_bps!r},  # All-in turnover cost in basis points.
    "ENTRY_SLIPPAGE_BPS": {CONFIG.entry_slippage_bps!r},  # Entry slippage in basis points.
    "STOP_SLIPPAGE_BPS": {CONFIG.stop_slippage_bps!r},  # Stop exit slippage in basis points.
    "TARGET_SLIPPAGE_BPS": {CONFIG.target_slippage_bps!r},  # Target exit slippage in basis points.
    "SQUAREOFF_SLIPPAGE_BPS": {CONFIG.squareoff_slippage_bps!r},  # Square-off slippage in basis points.

    # H) Portfolio-level risk management
    "DAILY_LOSS_LIMIT_PCT": {CONFIG.daily_loss_limit_pct!r},  # Optional daily loss block threshold.
    "BLOCK_NEW_TRADES_AFTER_DAILY_LOSS": {CONFIG.block_after_daily_loss!r},  # Block fresh trades after daily loss.
    "MIN_TRADES_FOR_GOAL": {CONFIG.min_trades_for_goal!r},  # Optional minimum sample-size goal.

    # I) Goals
    "MIN_RETURN_PCT": {CONFIG.min_return_pct!r},  # Goal: minimum return percent.
    "MAX_DRAWDOWN_PCT": {CONFIG.max_drawdown_pct!r},  # Goal: maximum drawdown percent.

    # J) Output settings
    "OUTPUT_DIR": "Strategy outputs",  # Report output folder; relative paths resolve under project root.
    "CREATE_TIMESTAMPED_OUTPUT_FOLDER": True,  # True creates run_YYYYMMDD_HHMMSS folders.
    "BACKTEST_OUTPUT_FOLDER_NAME": "BACKTEST_RESULTS",  # Used when timestamped output is False.
    "CLEAR_FIXED_OUTPUT_FOLDER": True,  # Clears fixed output folder before rerun.
    "CREATE_QUANTSTATS_REPORT": True,  # Saves QuantStats HTML when package is installed.
    "SAVE_EXCEL_SUMMARY": True,  # Saves Excel dashboard.
    "SAVE_SYMBOL_REPORTS": True,  # Saves per-symbol CSV/HTML reports.
    "SAVE_SELECTED_SYMBOL_REPORTS": True,  # Keeps selected symbol report folder.
    "PRINT_TOP_N": 20,  # Console top rows.
    "PRINT_BOTTOM_N": 10,  # Console risk-review rows.
    "MIN_TRADES_FOR_RANKING": 5,  # Minimum trades for ranking confidence.
    "MIN_WIN_RATE_FOR_A_GRADE": 55.0,  # A-grade win-rate threshold.
    "MIN_PROFIT_FACTOR_FOR_A_GRADE": 1.25,  # A-grade profit-factor threshold.
    "MAX_DRAWDOWN_FOR_A_GRADE_PCT": {CONFIG.max_drawdown_pct!r},  # A-grade drawdown threshold.
}}

STRATEGY_CONFIG = {strategy_config_literal}

OPTIMIZE_PARAMS = {{
    # Keep this small unless you are doing train/test or walk-forward checks.
    "target_rr": [STRATEGY_CONFIG["target_rr"]],
    "adx_min": [STRATEGY_CONFIG["adx_min"]],
    "volume_ratio_min": [STRATEGY_CONFIG["volume_ratio_min"]],
}}


# ============================================================
# 2) IMPORTS
# ============================================================

from datetime import datetime
from pathlib import Path
import itertools
import json
import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd

try:
    import quantstats as qs
    QUANTSTATS_AVAILABLE = True
except Exception:
    qs = None
    QUANTSTATS_AVAILABLE = False


# ============================================================
# 3) PROJECT ADAPTER
# ============================================================

def find_project_root(start: Path) -> Path:
    for folder in [start.parent, *start.parents]:
        if (folder / "engine.py").exists() and (folder / "project_config.py").exists():
            return folder
    raise RuntimeError("Could not find project root containing engine.py and project_config.py.")


PROJECT_ROOT = find_project_root(Path(__file__).resolve())
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import engine
import project_config
from project_config import ProjectConfig
from strategy import StrategyConfig


def direction_flags() -> tuple[bool, bool]:
    mode = str(CONFIG.get("DIRECTION_MODE", "both")).lower()
    if mode == "long":
        return True, False
    if mode == "short":
        return False, True
    return True, True


def project_config_values() -> dict:
    allow_long, allow_short = direction_flags()
    symbols = CONFIG.get("SYMBOLS") or ["UNKNOWN"]
    symbol = str(symbols[0])
    return {{
        "strategy_name": CONFIG["STRATEGY_NAME"],
        "symbol": symbol,
        "compare_symbol": CONFIG.get("COMPARE_SYMBOL"),
        "symbol_csv": CONFIG["SYMBOL_CSV"],
        "compare_csv": CONFIG.get("COMPARE_CSV"),
        "date_column": CONFIG["DATE_COLUMN"],
        "time_column": CONFIG["TIME_COLUMN"],
        "open_column": CONFIG["OPEN_COLUMN"],
        "high_column": CONFIG["HIGH_COLUMN"],
        "low_column": CONFIG["LOW_COLUMN"],
        "close_column": CONFIG["CLOSE_COLUMN"],
        "volume_column": CONFIG["VOLUME_COLUMN"],
        "start_date": CONFIG["BACKTEST_START_DATE"],
        "end_date": CONFIG["BACKTEST_END_DATE"],
        "timeframe": CONFIG["BACKTEST_TIME_FRAME"],
        "allocation": float(CONFIG["AMOUNT_INVESTED"]),
        "min_return_pct": float(CONFIG["MIN_RETURN_PCT"]),
        "max_drawdown_pct": float(CONFIG["MAX_DRAWDOWN_PCT"]),
        "session_start": CONFIG["MARKET_OPEN"],
        "opening_range_minutes": int(CONFIG["OPENING_RANGE_MINUTES"]),
        "breakout_start": CONFIG["STRATEGY_START"],
        "square_off_time": CONFIG["FORCE_EXIT"],
        "allow_long": allow_long,
        "allow_short": allow_short,
        "max_open_positions": int(CONFIG["MAX_POSITIONS"]),
        "cost_bps": float(CONFIG["COST_BPS"]),
        "candle_timestamp": CONFIG["CANDLE_TIMESTAMP"],
        "signal_evaluation_mode": CONFIG["SIGNAL_EVALUATION_MODE"],
        "entry_execution_mode": CONFIG["ENTRY_PRICE_MODE"],
        "same_candle_stop_target_policy": CONFIG["SAME_CANDLE_STOP_TARGET_POLICY"],
        "block_same_candle_reentry": bool(CONFIG["BLOCK_SAME_CANDLE_REENTRY"]),
        "allow_indicator_nan_trades": bool(CONFIG["ALLOW_INDICATOR_NAN_TRADES"]),
        "gap_through_stop_uses_open": bool(CONFIG["GAP_THROUGH_STOP_USES_OPEN"]),
        "entry_slippage_bps": float(CONFIG["ENTRY_SLIPPAGE_BPS"]),
        "stop_slippage_bps": float(CONFIG["STOP_SLIPPAGE_BPS"]),
        "target_slippage_bps": float(CONFIG["TARGET_SLIPPAGE_BPS"]),
        "squareoff_slippage_bps": float(CONFIG["SQUAREOFF_SLIPPAGE_BPS"]),
        "max_trades_per_day": CONFIG["MAX_TRADES_PER_DAY"],
        "daily_loss_limit_pct": CONFIG["DAILY_LOSS_LIMIT_PCT"],
        "block_after_daily_loss": bool(CONFIG["BLOCK_NEW_TRADES_AFTER_DAILY_LOSS"]),
        "min_trades_for_goal": int(CONFIG["MIN_TRADES_FOR_GOAL"]),
    }}


PROJECT_CONFIG = project_config_values()


def apply_project_config() -> None:
    global PROJECT_CONFIG
    PROJECT_CONFIG = project_config_values()
    cfg = ProjectConfig(**PROJECT_CONFIG)
    project_config.CONFIG = cfg
    engine.CONFIG = cfg
    engine.load_market_data.cache_clear()


def run_single_backtest(params: dict | None = None) -> dict:
    apply_project_config()
    values = dict(STRATEGY_CONFIG)
    if params:
        values.update(params)
    return engine.run_backtest(StrategyConfig(**values))


# ============================================================
# 4) REPORTING
# ============================================================

def safe_folder_name(value: str) -> str:
    text = str(value).strip().upper()
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in text).strip("_") or "UNKNOWN"


def resolve_output_base_dir() -> Path:
    output_dir = Path(str(CONFIG.get("OUTPUT_DIR", "Strategy outputs") or "Strategy outputs")).expanduser()
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    return output_dir


def prepare_output_run_dir() -> Path:
    base_dir = resolve_output_base_dir()
    base_dir.mkdir(parents=True, exist_ok=True)
    if CONFIG.get("CREATE_TIMESTAMPED_OUTPUT_FOLDER", True):
        run_dir = base_dir / f"run_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    else:
        run_dir = base_dir / str(CONFIG.get("BACKTEST_OUTPUT_FOLDER_NAME", "BACKTEST_RESULTS"))
        if CONFIG.get("CLEAR_FIXED_OUTPUT_FOLDER", False) and run_dir.exists():
            import shutil
            shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def trades_to_frame(result: dict) -> pd.DataFrame:
    rows = []
    for trade in result.get("trades", []):
        direction = str(trade["direction"]).lower()
        entry_price = float(trade["entry_price"])
        exit_price = float(trade["exit_price"])
        qty = int(trade["qty"])
        gross = (exit_price - entry_price) * qty
        if direction == "short":
            gross = -gross
        costs = (entry_price + exit_price) * qty * float(CONFIG["COST_BPS"]) / 10000
        net_pnl = float(trade["pnl"])
        entry_dt = pd.to_datetime(f"{{trade['date']}} {{trade['entry_time']}}")
        exit_dt = pd.to_datetime(f"{{trade['date']}} {{trade['exit_time']}}")
        holding_minutes = max((exit_dt - entry_dt).total_seconds() / 60, 0)
        rows.append({{
            "symbol": PROJECT_CONFIG["symbol"],
            "side": direction.upper(),
            "entry_time": entry_dt,
            "exit_time": exit_dt,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "qty": qty,
            "gross_pnl": gross,
            "costs": costs,
            "net_pnl": net_pnl,
            "return_on_capital_pct": net_pnl / float(CONFIG["INITIAL_CAPITAL"]),
            "exit_reason": trade.get("exit_reason"),
            "holding_minutes": holding_minutes,
        }})
    return pd.DataFrame(rows)


def equity_from_trades(trades_df: pd.DataFrame) -> pd.DataFrame:
    equity = float(CONFIG["INITIAL_CAPITAL"])
    rows = [{{"time": pd.to_datetime(PROJECT_CONFIG["start_date"]), "equity": equity}}]
    if trades_df.empty:
        return pd.DataFrame(rows)
    for _, row in trades_df.sort_values("exit_time").iterrows():
        equity += float(row["net_pnl"])
        rows.append({{"time": row["exit_time"], "equity": equity}})
    return pd.DataFrame(rows)


def max_consecutive(mask: pd.Series) -> int:
    best = current = 0
    for value in mask.fillna(False):
        current = current + 1 if bool(value) else 0
        best = max(best, current)
    return best


def calculate_metrics(trades_df: pd.DataFrame, equity_df: pd.DataFrame | None, label: str) -> dict:
    initial_capital = float(CONFIG["INITIAL_CAPITAL"])
    if trades_df is None or trades_df.empty:
        return {{"bucket": label, "total_trades": 0, "net_profit": 0.0, "net_profit_pct": 0.0,
                "win_rate_pct": 0.0, "profit_factor": None, "max_drawdown_pct": None}}
    pnl = trades_df["net_pnl"].astype(float)
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]
    gross_profit = float(wins.sum())
    gross_loss = float(losses.sum())
    profit_factor = abs(gross_profit / gross_loss) if gross_loss < 0 else (float("inf") if gross_profit > 0 else None)
    if equity_df is not None and not equity_df.empty and label == "OVERALL":
        eq = equity_df["equity"].astype(float)
        max_dd = ((eq / eq.cummax()) - 1).min() * 100
    else:
        side_eq = initial_capital + pnl.cumsum()
        max_dd = ((side_eq / side_eq.cummax()) - 1).min() * 100
    return {{
        "bucket": label,
        "total_trades": int(len(trades_df)),
        "winning_trades": int((pnl > 0).sum()),
        "losing_trades": int((pnl <= 0).sum()),
        "win_rate_pct": float((pnl > 0).mean() * 100),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "net_profit": float(pnl.sum()),
        "net_profit_pct": float(pnl.sum() / initial_capital * 100),
        "avg_trade_pnl": float(pnl.mean()),
        "median_trade_pnl": float(pnl.median()),
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "largest_win": float(pnl.max()),
        "largest_loss": float(pnl.min()),
        "profit_factor": profit_factor,
        "expectancy_per_trade": float(pnl.mean()),
        "avg_holding_minutes": float(trades_df["holding_minutes"].mean()) if "holding_minutes" in trades_df else None,
        "max_drawdown_pct": float(max_dd) if pd.notna(max_dd) else None,
        "max_consecutive_wins": max_consecutive(pnl > 0),
        "max_consecutive_losses": max_consecutive(pnl <= 0),
        "total_costs": float(trades_df["costs"].sum()) if "costs" in trades_df else 0.0,
    }}


def build_metrics_table(trades_df: pd.DataFrame, equity_df: pd.DataFrame) -> pd.DataFrame:
    rows = [calculate_metrics(trades_df, equity_df, "OVERALL")]
    if not trades_df.empty:
        rows.append(calculate_metrics(trades_df[trades_df["side"] == "LONG"].copy(), None, "LONG_ONLY"))
        rows.append(calculate_metrics(trades_df[trades_df["side"] == "SHORT"].copy(), None, "SHORT_ONLY"))
        rows.append(calculate_metrics(trades_df.copy(), None, f"SYMBOL_{{PROJECT_CONFIG['symbol']}}"))
    return pd.DataFrame(rows)


def build_leaderboard(trades_df: pd.DataFrame, metrics_df: pd.DataFrame) -> pd.DataFrame:
    overall = metrics_df[metrics_df["bucket"] == "OVERALL"].iloc[0].to_dict()
    total_trades = int(overall.get("total_trades", 0) or 0)
    win_rate = float(overall.get("win_rate_pct", 0) or 0)
    pf = overall.get("profit_factor")
    pf_score = 10.0 if pf == float("inf") else float(pf or 0)
    max_dd = abs(float(overall.get("max_drawdown_pct", 0) or 0))
    net_profit_pct = float(overall.get("net_profit_pct", 0) or 0)
    if total_trades == 0:
        decision, action, reason, risk_flags = "NO_TRADES", "IGNORE", "No trades generated", 0
    elif net_profit_pct >= CONFIG["MIN_RETURN_PCT"] and max_dd <= CONFIG["MAX_DRAWDOWN_PCT"] and win_rate >= CONFIG["MIN_WIN_RATE_FOR_A_GRADE"] and pf_score >= CONFIG["MIN_PROFIT_FACTOR_FOR_A_GRADE"]:
        decision, action, reason, risk_flags = "A_GRADE", "TRADE_CANDIDATE", "Passes profit + risk filters", 0
    elif net_profit_pct > 0 and max_dd <= CONFIG["MAX_DRAWDOWN_PCT"]:
        decision, action, reason, risk_flags = "B_GRADE", "WATCHLIST", "Positive but below one or more A-grade filters", 1
    else:
        decision, action, reason, risk_flags = "REJECT", "AVOID", "Failed profit or risk filters", 2
    ranking_score = net_profit_pct * 2 + win_rate * 0.10 + min(pf_score, 10) * 3 - max_dd * 1.5 + min(total_trades / 15, 1) * 10
    return pd.DataFrame([{{
        "rank": 1,
        "symbol": PROJECT_CONFIG["symbol"],
        "status": "OK",
        "error": "",
        "candles": None,
        "total_trades": total_trades,
        "winning_trades": overall.get("winning_trades", 0),
        "losing_trades": overall.get("losing_trades", 0),
        "win_rate_pct": win_rate,
        "net_profit": overall.get("net_profit", 0),
        "net_profit_pct": net_profit_pct,
        "largest_win": overall.get("largest_win", 0),
        "largest_loss": overall.get("largest_loss", 0),
        "profit_factor": pf,
        "max_drawdown_pct": overall.get("max_drawdown_pct"),
        "max_consecutive_losses": overall.get("max_consecutive_losses", 0),
        "max_consecutive_wins": overall.get("max_consecutive_wins", 0),
        "final_decision": decision,
        "action": action,
        "reason": reason,
        "risk_flag_count": risk_flags,
        "ranking_score": ranking_score,
    }}])


def build_analytics_tables(trades_df: pd.DataFrame, leaderboard_df: pd.DataFrame) -> dict:
    if trades_df.empty:
        empty = pd.DataFrame()
        return {{"daily_pnl": empty, "monthly_pnl": empty, "exit_reason_analysis": empty,
                "side_analysis": empty, "decision_summary": leaderboard_df["final_decision"].value_counts().reset_index()}}
    temp = trades_df.copy()
    temp["exit_date"] = pd.to_datetime(temp["exit_time"]).dt.date
    temp["exit_month"] = pd.to_datetime(temp["exit_time"]).dt.to_period("M").astype(str)
    temp["is_win"] = temp["net_pnl"].astype(float) > 0
    daily = temp.groupby(["exit_date", "symbol"], dropna=False).agg(
        trades=("net_pnl", "size"), wins=("is_win", "sum"), net_pnl=("net_pnl", "sum"),
        avg_pnl=("net_pnl", "mean"), largest_loss=("net_pnl", "min"), largest_win=("net_pnl", "max")
    ).reset_index()
    daily["win_rate_pct"] = np.where(daily["trades"] > 0, daily["wins"] / daily["trades"] * 100, 0)
    monthly = temp.groupby(["exit_month", "symbol"], dropna=False).agg(
        trades=("net_pnl", "size"), wins=("is_win", "sum"), net_pnl=("net_pnl", "sum"),
        avg_pnl=("net_pnl", "mean"), largest_loss=("net_pnl", "min"), largest_win=("net_pnl", "max")
    ).reset_index()
    monthly["win_rate_pct"] = np.where(monthly["trades"] > 0, monthly["wins"] / monthly["trades"] * 100, 0)
    exit_reason = temp.groupby(["symbol", "exit_reason"], dropna=False).agg(
        trades=("net_pnl", "size"), wins=("is_win", "sum"), net_pnl=("net_pnl", "sum"),
        avg_pnl=("net_pnl", "mean"), largest_loss=("net_pnl", "min"), largest_win=("net_pnl", "max")
    ).reset_index()
    exit_reason["win_rate_pct"] = np.where(exit_reason["trades"] > 0, exit_reason["wins"] / exit_reason["trades"] * 100, 0)
    side = temp.groupby(["symbol", "side"], dropna=False).agg(
        trades=("net_pnl", "size"), wins=("is_win", "sum"), net_pnl=("net_pnl", "sum"),
        avg_pnl=("net_pnl", "mean"), largest_loss=("net_pnl", "min"), largest_win=("net_pnl", "max")
    ).reset_index()
    side["win_rate_pct"] = np.where(side["trades"] > 0, side["wins"] / side["trades"] * 100, 0)
    decision_summary = leaderboard_df.groupby(["final_decision", "action"], dropna=False).agg(
        symbols=("symbol", "count"), avg_net_profit=("net_profit", "mean"),
        total_net_profit=("net_profit", "sum"), avg_win_rate_pct=("win_rate_pct", "mean")
    ).reset_index()
    return {{"daily_pnl": daily, "monthly_pnl": monthly, "exit_reason_analysis": exit_reason,
            "side_analysis": side, "decision_summary": decision_summary}}


def build_dashboard_kpis(metrics_df: pd.DataFrame, leaderboard_df: pd.DataFrame) -> pd.DataFrame:
    overall = metrics_df[metrics_df["bucket"] == "OVERALL"].iloc[0].to_dict()
    rows = [
        ("initial_capital", CONFIG["INITIAL_CAPITAL"]),
        ("symbols_tested", len(leaderboard_df)),
        ("a_grade_symbols", int((leaderboard_df["final_decision"] == "A_GRADE").sum())),
        ("overall_total_trades", overall.get("total_trades")),
        ("overall_win_rate_pct", overall.get("win_rate_pct")),
        ("overall_net_profit", overall.get("net_profit")),
        ("overall_net_profit_pct", overall.get("net_profit_pct")),
        ("overall_profit_factor", overall.get("profit_factor")),
        ("overall_max_drawdown_pct", overall.get("max_drawdown_pct")),
    ]
    return pd.DataFrame([{{"metric": key, "value": value}} for key, value in rows])


def save_quantstats_report(trades_df: pd.DataFrame, output_path: Path, title: str) -> None:
    if not QUANTSTATS_AVAILABLE or trades_df.empty:
        return
    daily = trades_df.copy()
    daily["exit_date"] = pd.to_datetime(daily["exit_time"]).dt.date
    returns = daily.groupby("exit_date")["net_pnl"].sum()
    returns.index = pd.to_datetime(returns.index)
    returns = returns / float(CONFIG["INITIAL_CAPITAL"])
    try:
        qs.reports.html(returns, benchmark=None, output=str(output_path), title=title)
    except Exception as exc:
        print(f"Could not create QuantStats report {{output_path}}: {{exc}}")


def save_excel_dashboard(excel_path: Path, dashboard_df: pd.DataFrame, leaderboard_df: pd.DataFrame,
                         metrics_df: pd.DataFrame, trades_df: pd.DataFrame, analytics: dict,
                         data_quality_df: pd.DataFrame) -> None:
    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            dashboard_df.to_excel(writer, sheet_name="Dashboard", index=False)
            leaderboard_df.to_excel(writer, sheet_name="Leaderboard", index=False)
            leaderboard_df[leaderboard_df["final_decision"].isin(["A_GRADE", "B_GRADE"])].to_excel(writer, sheet_name="Trade Candidates", index=False)
            leaderboard_df[leaderboard_df["final_decision"].isin(["REJECT", "DATA_FAILED", "LOW_SAMPLE"])].to_excel(writer, sheet_name="Avoid Review", index=False)
            metrics_df.to_excel(writer, sheet_name="Overall Metrics", index=False)
            analytics.get("decision_summary", pd.DataFrame()).to_excel(writer, sheet_name="Decision Summary", index=False)
            analytics.get("daily_pnl", pd.DataFrame()).to_excel(writer, sheet_name="Daily PnL", index=False)
            analytics.get("monthly_pnl", pd.DataFrame()).to_excel(writer, sheet_name="Monthly PnL", index=False)
            analytics.get("exit_reason_analysis", pd.DataFrame()).to_excel(writer, sheet_name="Exit Analysis", index=False)
            analytics.get("side_analysis", pd.DataFrame()).to_excel(writer, sheet_name="Long Short", index=False)
            data_quality_df.to_excel(writer, sheet_name="Data Quality", index=False)
            pd.DataFrame([{{"parameter": k, "value": str(v)}} for k, v in CONFIG.items()]).to_excel(writer, sheet_name="Config", index=False)
            trades_df.to_excel(writer, sheet_name="All Trades", index=False)
        print(f"Saved Excel dashboard: {{excel_path}}")
    except Exception as exc:
        print(f"Could not save Excel dashboard. Reason: {{exc}}")


def save_reports(result: dict) -> dict:
    trades_df = trades_to_frame(result)
    equity_df = equity_from_trades(trades_df)
    metrics_df = build_metrics_table(trades_df, equity_df)
    leaderboard_df = build_leaderboard(trades_df, metrics_df)
    data_quality_df = pd.DataFrame([{{
        "symbol": PROJECT_CONFIG["symbol"], "status": "OK", "error": "", "candles": None,
        "first_candle": PROJECT_CONFIG["start_date"], "last_candle": PROJECT_CONFIG["end_date"],
    }}])
    analytics = build_analytics_tables(trades_df, leaderboard_df)
    dashboard_df = build_dashboard_kpis(metrics_df, leaderboard_df)

    run_dir = prepare_output_run_dir()
    read_first_dir = run_dir / "00_READ_FIRST"
    excel_dir = run_dir / "01_EXCEL_DASHBOARD"
    csv_dir = run_dir / "02_MASTER_CSVS"
    reports_dir = run_dir / "03_SELECTED_SYMBOL_REPORTS" / safe_folder_name(PROJECT_CONFIG["symbol"])
    reviews_dir = run_dir / "04_SELECTED_REVIEWS"
    for folder in [read_first_dir, excel_dir, csv_dir, reports_dir, reviews_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    paths = {{
        "run_dir": str(run_dir),
        "run_summary_txt": str(read_first_dir / "RUN_SUMMARY.txt"),
        "top_trade_candidates_csv": str(read_first_dir / "top_trade_candidates.csv"),
        "avoid_or_review_csv": str(read_first_dir / "avoid_or_review.csv"),
        "no_trade_symbols_csv": str(read_first_dir / "no_trade_symbols.csv"),
        "excel_dashboard": str(excel_dir / "backtest_dashboard.xlsx"),
        "master_leaderboard_csv": str(csv_dir / "master_leaderboard.csv"),
        "all_trades_csv": str(csv_dir / "all_trades.csv"),
        "overall_metrics_csv": str(csv_dir / "overall_metrics.csv"),
        "data_quality_csv": str(csv_dir / "data_quality.csv"),
        "daily_pnl_by_symbol_csv": str(csv_dir / "daily_pnl_by_symbol.csv"),
        "monthly_pnl_by_symbol_csv": str(csv_dir / "monthly_pnl_by_symbol.csv"),
        "exit_reason_analysis_csv": str(csv_dir / "exit_reason_analysis.csv"),
        "long_short_analysis_csv": str(csv_dir / "long_short_analysis.csv"),
        "decision_summary_csv": str(csv_dir / "decision_summary.csv"),
        "selected_symbol_reports_dir": str(reports_dir.parent),
        "symbol_trades_csv": str(reports_dir / "trades.csv"),
        "symbol_performance_metrics_csv": str(reports_dir / "performance_metrics.csv"),
        "symbol_quant_tearsheet_html": str(reports_dir / "quant_tearsheet.html"),
    }}

    leaderboard_df.to_csv(paths["master_leaderboard_csv"], index=False)
    trades_df.to_csv(paths["all_trades_csv"], index=False)
    metrics_df.to_csv(paths["overall_metrics_csv"], index=False)
    data_quality_df.to_csv(paths["data_quality_csv"], index=False)
    analytics["daily_pnl"].to_csv(paths["daily_pnl_by_symbol_csv"], index=False)
    analytics["monthly_pnl"].to_csv(paths["monthly_pnl_by_symbol_csv"], index=False)
    analytics["exit_reason_analysis"].to_csv(paths["exit_reason_analysis_csv"], index=False)
    analytics["side_analysis"].to_csv(paths["long_short_analysis_csv"], index=False)
    analytics["decision_summary"].to_csv(paths["decision_summary_csv"], index=False)
    leaderboard_df[leaderboard_df["final_decision"].isin(["A_GRADE", "B_GRADE", "C_GRADE"])].to_csv(paths["top_trade_candidates_csv"], index=False)
    leaderboard_df[leaderboard_df["final_decision"].isin(["REJECT", "LOW_SAMPLE", "DATA_FAILED"])].to_csv(paths["avoid_or_review_csv"], index=False)
    leaderboard_df[leaderboard_df["final_decision"] == "NO_TRADES"].to_csv(paths["no_trade_symbols_csv"], index=False)
    trades_df.to_csv(paths["symbol_trades_csv"], index=False)
    metrics_df.to_csv(paths["symbol_performance_metrics_csv"], index=False)
    save_quantstats_report(trades_df, Path(paths["symbol_quant_tearsheet_html"]), f"Intraday Strategy - {{PROJECT_CONFIG['symbol']}}")
    if CONFIG.get("SAVE_EXCEL_SUMMARY", True):
        save_excel_dashboard(Path(paths["excel_dashboard"]), dashboard_df, leaderboard_df, metrics_df, trades_df, analytics, data_quality_df)

    lines = [
        "BACKTEST OUTPUT SUMMARY",
        "=" * 80,
        f"Created at: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}",
        f"Symbol: {{PROJECT_CONFIG['symbol']}}",
        f"Period: {{PROJECT_CONFIG['start_date']}} to {{PROJECT_CONFIG['end_date']}}",
        f"Return %: {{result['return_pct']:.4f}}",
        f"Max drawdown %: {{result['max_drawdown_pct']:.4f}}",
        f"Trades: {{result['num_trades']}}",
        f"Win rate %: {{result['win_rate_pct']:.2f}}",
        f"Profit factor: {{result['profit_factor']:.4f}}",
        f"Goal pass: {{result['goal_pass']}}",
        "",
        "HOW TO READ THIS OUTPUT",
        "-" * 80,
        "1. Open 00_READ_FIRST/top_trade_candidates.csv first.",
        "2. Then open 01_EXCEL_DASHBOARD/backtest_dashboard.xlsx.",
        "3. Review 02_MASTER_CSVS/all_trades.csv and overall_metrics.csv.",
        "4. Open 03_SELECTED_SYMBOL_REPORTS/<SYMBOL>/ for symbol-level trades and metrics.",
    ]
    Path(paths["run_summary_txt"]).write_text("\\n".join(lines), encoding="utf-8")

    print("\\n" + "=" * 100)
    print("PORTFOLIO SCAN DASHBOARD")
    print("=" * 100)
    print(leaderboard_df[["rank", "symbol", "final_decision", "action", "total_trades", "win_rate_pct", "net_profit_pct", "profit_factor", "max_drawdown_pct", "ranking_score", "reason"]].to_string(index=False))
    print(f"\\nSaved report folder: {{run_dir}}")
    return paths


# ============================================================
# 5) BACKTEST / OPTIMIZER
# ============================================================

def optimize() -> list[dict]:
    keys = list(OPTIMIZE_PARAMS)
    results = []
    for combo in itertools.product(*(OPTIMIZE_PARAMS[key] for key in keys)):
        params = dict(zip(keys, combo))
        result = run_single_backtest(params)
        results.append({{"params": params, "result": result}})
    return sorted(
        results,
        key=lambda item: (item["result"]["goal_pass"], item["result"]["return_pct"], -item["result"]["max_drawdown_pct"]),
        reverse=True,
    )


def main() -> None:
    if CONFIG["RUN_OPTIMIZATION"]:
        rows = optimize()
        for idx, row in enumerate(rows[:20], start=1):
            result = row["result"]
            print(f"{{idx:03d}} return={{result['return_pct']:.4f}} dd={{result['max_drawdown_pct']:.4f}} trades={{result['num_trades']}} params={{row['params']}}")
        return

    result = run_single_backtest()
    report_paths = save_reports(result)
    print("---")
    print(f"file:               {strategy_file_name}")
    print(f"kept_rank:          {rank:03d}")
    print(f"commit:             {commit}")
    print(f"description:        {description}")
    print(f"strategy_name:      {{PROJECT_CONFIG['strategy_name']}}")
    print(f"symbol:             {{PROJECT_CONFIG['symbol']}}")
    print(f"compare:            {{PROJECT_CONFIG['compare_symbol']}}")
    print(f"period:             {{PROJECT_CONFIG['start_date']}} to {{PROJECT_CONFIG['end_date']}}")
    print(f"timeframe:          {{PROJECT_CONFIG['timeframe']}}")
    print(f"allocation:         {{PROJECT_CONFIG['allocation']:.0f}}")
    print(f"entry_mode:         {{PROJECT_CONFIG['entry_execution_mode']}}")
    print(f"return_pct:         {{result['return_pct']:.4f}}")
    print(f"max_drawdown_pct:   {{result['max_drawdown_pct']:.4f}}")
    print(f"net_pnl:            {{result['net_pnl']:.2f}}")
    print(f"num_trades:         {{result['num_trades']}}")
    print(f"win_rate_pct:       {{result['win_rate_pct']:.2f}}")
    print(f"profit_factor:      {{result['profit_factor']:.4f}}")
    print(f"goal_pass:          {{result['goal_pass']}}")
    print(f"report_folder:      {{report_paths['run_dir']}}")
    print("strategy_config_json:")
    print(json.dumps(result["config"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
'''


def export_kept_strategy_artifacts(
    rank: int,
    commit: str,
    description: str,
    strategy: StrategyConfig,
    result: dict,
) -> None:
    folder = KEPT_DIR / f"{rank:03d}_{result['return_pct']:.4f}_return"
    folder.mkdir(parents=True, exist_ok=True)

    show = _run(["git", "show", f"{commit}:strategy.py"])
    if show.returncode == 0:
        strategy_text = show.stdout
    elif commit.startswith("manual"):
        strategy_text = (ROOT / "strategy.py").read_text()
    else:
        raise RuntimeError(show.stderr)

    (folder / f"Strategy_{rank:03d}.py").write_text(strategy_text)
    (folder / f"README_{rank:03d}.md").write_text(_readme(rank, commit, description, strategy, result))
    backtest_name = f"{_safe_name(CONFIG.strategy_name)}_Backtest_{rank:03d}.py"
    (folder / backtest_name).write_text(_backtesting_script(rank, commit, description, strategy, result))
    _write_root_readme()
