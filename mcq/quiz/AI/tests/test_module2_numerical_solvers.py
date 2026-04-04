from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from numerical_solvers import (
    forward_payoff,
    futures_daily_mtm,
    futures_margin_call,
    long_call_profit,
    long_put_profit_threshold,
)


def test_forward_payoff_matches_pdf_example():
    result = forward_payoff(100, "1792.13", "1780.50")
    assert result["final_answer"] == Decimal("-1163.00")
    assert result["intermediate_steps"]["payoff_per_unit"] == Decimal("-11.63")


def test_forward_payoff_zero_at_breakeven():
    result = forward_payoff(100, "64", "64")
    assert result["final_answer"] == Decimal("0")


def test_futures_daily_mtm_matches_pdf_example():
    result = futures_daily_mtm(100, "1792.13", "1797.13", "4950")
    assert result["intermediate_steps"]["day_gain_loss"] == Decimal("500.00")
    assert result["final_answer"] == Decimal("5450.00")


def test_futures_margin_call_matches_pdf_example():
    result = futures_margin_call("4950", "4500", "4450")
    assert result["final_answer"] == Decimal("500")


def test_futures_margin_call_zero_when_above_maintenance():
    result = futures_margin_call("4950", "4500", "4544")
    assert result["final_answer"] == Decimal("0")


def test_long_call_profit_matches_pdf_example():
    result = long_call_profit("50", "45", "6")
    assert result["intermediate_steps"]["payoff"] == Decimal("5")
    assert result["final_answer"] == Decimal("-1")


def test_long_put_profit_threshold_matches_pdf_rule():
    result = long_put_profit_threshold("45", "6")
    assert result["final_answer"] == Decimal("39")
