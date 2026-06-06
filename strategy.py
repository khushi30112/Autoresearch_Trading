"""
Editable strategy configuration.

Autoresearch experiments should edit this file. Project-specific settings such
as symbol, date range, allocation, and CSV paths live in project_config.py.
"""

from dataclasses import dataclass


@dataclass
class StrategyConfig:
    # Entry behavior
    entry_price: str = "trigger"  # trigger or close
    breakout_buffer_pct: float = 0.00
    breakout_atr_mult: float = 0.00
    max_reentries: int = 1

    # Filters
    avoid_open_beyond_prev_day: bool = False
    adx_min: float = 0.0
    atr_pct_min: float = 0.0
    atr_pct_max: float = 999.0
    volume_ratio_min: float = 0.0
    use_dmi: bool = False
    ema_filter: bool = False
    long_slope_min: float = -999.0
    short_slope_min: float = -999.0
    long_rel_strength_min: float = -999.0
    short_rel_strength_min: float = -999.0

    # Risk management
    stop_mode: str = "orb"  # orb, atr, percent
    stop_loss_pct: float = 0.70
    min_stop_pct: float = 0.15
    atr_stop_mult: float = 1.20
    target_rr: float = 1.00
    trailing_mode: str = "none"  # none, atr, percent
    atr_trail_mult: float = 1.60
    trailing_pct: float = 0.50


def get_config() -> StrategyConfig:
    return StrategyConfig()
