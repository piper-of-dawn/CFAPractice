from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from numerical_solvers import (
    accrued_interest,
    bond_price_coupon_date,
    flat_price_from_full_price,
    full_price_between_coupons,
    implied_rate_lump_sum,
    interpolated_yield,
)


def test_bond_price_coupon_date_matches_module6_discount_example():
    result = bond_price_coupon_date("1.6", "0.02", 10, "100")
    assert result["rounded_answer"] == Decimal("96.407")


def test_bond_price_coupon_date_matches_module6_par_example():
    result = bond_price_coupon_date("1.6", "0.016", 10, "100")
    assert result["rounded_answer"] == Decimal("100.000")


def test_bond_price_coupon_date_matches_module6_premium_example():
    result = bond_price_coupon_date("1.6", "0.012", 10, "100")
    assert result["rounded_answer"] == Decimal("103.748")


def test_zero_coupon_negative_ytm_matches_module6_example():
    result = implied_rate_lump_sum("100.763", "100", 5)
    assert result["rounded_answer"] == Decimal("-0.0015")


def test_accrued_interest_actual_actual_matches_module6_example():
    result = accrued_interest("2.3125", 43, 184)
    assert result["rounded_answer"] == Decimal("0.540")


def test_accrued_interest_30_360_matches_module6_example():
    result = accrued_interest("2.3125", 42, 180)
    assert result["rounded_answer"] == Decimal("0.540")


def test_full_and_flat_price_brwa_between_coupons_match_module6_example():
    full = full_price_between_coupons("96.735", "0.02", 90, 180)
    flat = flat_price_from_full_price(full["final_answer"], "0.80")
    assert full["rounded_answer"] == Decimal("97.698")
    assert flat["rounded_answer"] == Decimal("96.898")


def test_full_and_flat_price_romania_match_module6_example():
    full = full_price_between_coupons("114.838", "0.035", 256, 366)
    flat = flat_price_from_full_price(full["final_answer"], "3.235")
    assert full["rounded_answer"] == Decimal("117.635")
    assert flat["rounded_answer"] == Decimal("114.400")


def test_full_price_actual_actual_12_percent_bond_matches_module6_example():
    full = full_price_between_coupons("108.584", "0.0975", 131, 365)
    assert full["rounded_answer"] == Decimal("112.271")


def test_interpolated_yield_matches_module6_matrix_pricing_example():
    result = interpolated_yield(2, 5, 3, "0.038035", "0.041885")
    assert result["rounded_answer"] == Decimal("0.039318")
