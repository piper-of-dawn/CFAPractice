from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from numerical_solvers import (
    future_value_lump_sum,
    implied_rate_lump_sum,
    present_value_lump_sum,
    present_value_lump_sum_non_annual,
)


def test_future_value_lump_sum_simple_growth():
    result = future_value_lump_sum("100", "0.05", 2)
    assert result["final_answer"] == Decimal("110.25")
    assert result["intermediate_steps"]["growth_factor"] == Decimal("1.1025")


def test_present_value_lump_sum_discount_bond_example():
    result = present_value_lump_sum("100", "0.067", 20)
    assert result["rounded_answer"] == Decimal("27.33")


def test_present_value_lump_sum_negative_rate_example():
    result = present_value_lump_sum("100", "-0.0005", 10)
    assert result["rounded_answer"] == Decimal("100.50")


def test_present_value_lump_sum_non_annual_matches_gic_example():
    result = present_value_lump_sum_non_annual("5000000", "0.06", 12, 10)
    assert result["rounded_answer"] == Decimal("2748163.67")
    assert result["intermediate_steps"]["periodic_rate"] == Decimal("0.005")
    assert result["intermediate_steps"]["total_periods"] == 120


def test_implied_rate_lump_sum_discount_bond_example():
    result = implied_rate_lump_sum("22.68224", "100", 20)
    assert result["rounded_answer"] == Decimal("0.0770")


def test_implied_rate_lump_sum_shorter_period_example():
    result = implied_rate_lump_sum("95.72", "100", 4)
    assert result["rounded_answer"] == Decimal("0.0110")
