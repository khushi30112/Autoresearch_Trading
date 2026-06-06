from __future__ import annotations

import json

from engine import run_backtest
from project_config import CONFIG
from strategy import get_config


def main() -> None:
    strategy = get_config()
    result = run_backtest(strategy)

    print("---")
    print(f"strategy_name:      {CONFIG.strategy_name}")
    print(f"symbol:             {CONFIG.symbol}")
    print(f"compare:            {CONFIG.compare_symbol}")
    print(f"period:             {CONFIG.start_date} to {CONFIG.end_date}")
    print(f"timeframe:          {CONFIG.timeframe}")
    print(f"allocation:         {CONFIG.allocation:.0f}")
    print(f"opening_range_min:  {CONFIG.opening_range_minutes}")
    print(f"return_pct:         {result['return_pct']:.4f}")
    print(f"max_drawdown_pct:   {result['max_drawdown_pct']:.4f}")
    print(f"net_pnl:            {result['net_pnl']:.2f}")
    print(f"num_trades:         {result['num_trades']}")
    print(f"win_rate_pct:       {result['win_rate_pct']:.2f}")
    print(f"profit_factor:      {result['profit_factor']:.4f}")
    print(f"symbol_bh_pct:      {result['symbol_buy_hold_pct']:.4f}")
    print(f"goal_pass:          {result['goal_pass']}")
    print("config_json:")
    print(json.dumps(result["config"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
