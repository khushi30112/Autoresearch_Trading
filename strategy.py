"""
Editable strategy configuration.

Autoresearch experiments should edit this file. Project-specific settings such
as symbol, date range, allocation, and CSV paths live in project_config.py.
"""

from dataclasses import dataclass


@dataclass
class StrategyConfig:
    # Entry behavior
    entry_price: str = "trigger"  # Strategy entry preference; project entry mode still controls final fill model.
    breakout_buffer_pct: float = 0.00  # Extra breakout buffer as percent of close.
    breakout_atr_mult: float = 0.00  # Extra breakout buffer as ATR multiple; max of pct/ATR buffer is used.
    max_reentries: int = 1  # Max entries per direction per day; engine still allows only one open position.

    # Filters
    avoid_open_beyond_prev_day: bool = False  # Skip day if open is outside previous day high/low.
    adx_min: float = 0.0  # Minimum ADX14; 0 disables this filter.
    atr_pct_min: float = 0.0  # Minimum ATR14 percent; 0 disables lower volatility filter.
    atr_pct_max: float = 999.0  # Maximum ATR14 percent; 999 disables upper volatility filter.
    volume_ratio_min: float = 0.0  # Minimum volume/SMA20 volume ratio; 0 disables this filter.
    use_dmi: bool = False  # Require +DI > -DI for longs and -DI > +DI for shorts.
    ema_filter: bool = False  # Require close above EMA20 for longs and below EMA20 for shorts.
    long_slope_min: float = -999.0  # Minimum normalized slope12 for longs; -999 disables.
    short_slope_min: float = -999.0  # Minimum bearish normalized slope12 magnitude for shorts; -999 disables.
    long_rel_strength_min: float = -999.0  # Minimum symbol-vs-compare intraday strength for longs.
    short_rel_strength_min: float = -999.0  # Minimum bearish relative weakness magnitude for shorts.

    # Risk management
    stop_mode: str = "orb"  # Initial stop mode: orb, atr, or percent.
    stop_loss_pct: float = 0.70  # Percent stop distance when stop_mode is percent.
    min_stop_pct: float = 0.15  # Minimum stop distance as percent of entry for ATR stops.
    atr_stop_mult: float = 1.20  # ATR14 multiple when stop_mode is atr.
    target_rr: float = 1.00  # Target as reward/risk multiple; <=0 disables target.
    trailing_mode: str = "none"  # Trailing stop mode: none, atr, or percent.
    atr_trail_mult: float = 1.60  # ATR14 multiple for ATR trailing stop.
    trailing_pct: float = 0.50  # Percent trailing distance for percent trailing stop.


def get_config() -> StrategyConfig:
    return StrategyConfig()
