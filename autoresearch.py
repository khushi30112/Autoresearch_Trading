"""
Generic keep/reject autoresearch runner.

Edit CANDIDATES or generate_candidates() with your own ideas. Every kept
strategy is committed and exported into kept_strategies/<rank>/ with a README.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import asdict
from pathlib import Path

from engine import run_backtest
from exporters import export_kept_strategy_artifacts
from project_config import CONFIG
from strategy import StrategyConfig


ROOT = Path(__file__).resolve().parent
STRATEGY = ROOT / "strategy.py"
RESULTS = ROOT / "results.tsv"
KEPT_DIR = ROOT / "kept_strategies"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def fmt(value: object) -> str:
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def write_strategy(values: dict[str, object]) -> None:
    text = STRATEGY.read_text()
    for key, value in values.items():
        pattern = rf"({key}:\s*[^=]+=\s*)([^#\n]+)"
        text, count = re.subn(pattern, rf"\g<1>{fmt(value)}", text)
        if count != 1:
            raise RuntimeError(f"Could not update {key}; matched {count} lines")
    STRATEGY.write_text(text)


def short_head() -> str:
    result = run(["git", "rev-parse", "--short", "HEAD"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def generate_candidates() -> list[tuple[str, dict[str, object]]]:
    return [
        ("baseline", {}),
        ("increase target to 1.1R", {"target_rr": 1.1}),
        ("lower target to 0.9R", {"target_rr": 0.9}),
        ("enable ADX 18 filter", {"adx_min": 18.0}),
        ("enable DMI filter", {"use_dmi": True}),
        ("volume ratio 1.0", {"volume_ratio_min": 1.0}),
        ("ATR percent minimum 0.10", {"atr_pct_min": 0.10}),
        ("max reentries 2", {"max_reentries": 2}),
        ("max reentries 3", {"max_reentries": 3}),
        ("EMA filter", {"ema_filter": True}),
        ("avoid open outside previous day range", {"avoid_open_beyond_prev_day": True}),
    ]


def main() -> None:
    if not RESULTS.exists():
        RESULTS.write_text("commit\treturn_pct\tmax_drawdown_pct\tstatus\tdescription\n")
    KEPT_DIR.mkdir(exist_ok=True)

    best_return = float("-inf")
    best_dd = float("inf")
    kept_rank = len([p for p in KEPT_DIR.iterdir() if p.is_dir()])
    base = asdict(StrategyConfig())

    for idx, (description, overrides) in enumerate(generate_candidates(), start=1):
        values = dict(base)
        values.update(overrides)
        write_strategy(values)
        add = run(["git", "add", "strategy.py"])
        if add.returncode != 0:
            raise RuntimeError(add.stderr)
        commit = run(["git", "commit", "-m", f"Experiment {idx:03d} {description}"])
        if commit.returncode != 0 and "nothing to commit" in (commit.stdout + commit.stderr):
            continue
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr)
        chash = short_head()

        strategy = StrategyConfig(**values)
        result = run_backtest(strategy)
        improved = result["goal_pass"] and (
            result["return_pct"] > best_return
            or (result["return_pct"] == best_return and result["max_drawdown_pct"] < best_dd)
        )
        status = "keep" if improved else "discard"
        with RESULTS.open("a", newline="") as f:
            f.write(f"{chash}\t{result['return_pct']:.4f}\t{result['max_drawdown_pct']:.4f}\t{status}\t{description}\n")

        if improved:
            best_return = result["return_pct"]
            best_dd = result["max_drawdown_pct"]
            kept_rank += 1
            export_kept_strategy_artifacts(kept_rank, chash, description, strategy, result)
            run(["git", "add", "results.tsv", "kept_strategies"]).check_returncode()
            run(["git", "commit", "-m", f"Export kept strategy {kept_rank:03d}"]).check_returncode()
        else:
            run(["git", "reset", "--hard", "HEAD~1"]).check_returncode()


if __name__ == "__main__":
    main()
