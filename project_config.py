"""
Project-level settings for a generic trading autoresearch run.

Edit this file to point the framework at any scrip/instrument and date range.
Strategy experiments should normally edit strategy.py only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ProjectConfig:
    # Identity and data
    strategy_name: str = "Open Range Breakout"
    symbol: str = "YOUR_SYMBOL"
    compare_symbol: str | None = None
    symbol_csv: str = "data/YOUR_SYMBOL_5m.csv"
    compare_csv: str | None = None

    # CSV schema
    date_column: str = "date"
    time_column: str = "time"
    open_column: str = "open"
    high_column: str = "high"
    low_column: str = "low"
    close_column: str = "close"
    volume_column: str = "volume"

    # Backtest range and timeframe label
    start_date: str = "2026-01-01"
    end_date: str = "2026-04-30"
    timeframe: str = "5min"

    # Capital and goals
    allocation: float = 600_000.0
    min_return_pct: float = 12.0
    max_drawdown_pct: float = 5.0

    # Session and ORB timing
    session_start: str = "09:15:00"
    opening_range_minutes: int = 10
    breakout_start: str = "09:25:00"
    square_off_time: str = "15:20:00"

    # Trade permissions
    allow_long: bool = True
    allow_short: bool = True
    max_open_positions: int = 1

    # Execution assumptions
    cost_bps: float = 3.0

    def symbol_path(self) -> Path:
        return ROOT / self.symbol_csv

    def compare_path(self) -> Path | None:
        return ROOT / self.compare_csv if self.compare_csv else None


CONFIG = ProjectConfig()
