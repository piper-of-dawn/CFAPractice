from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from numerical_solvers import (
    annual_yield_from_periodic_rate,
    convert_apr_periodicity,
    current_yield_from_rate_and_price,
    g_spread_bps,
    government_equivalent_yield,
    simple_yield,
)


def test_annual_yield_from_periodic_rate_matches_semiannual_bond_basis_rule():
    result = annual_yield_from_periodic_rate("0.02", 2)
    assert result["final_answer"] == Decimal("0.04")


def test_convert_apr_periodicity_matches_pdf_quarterly_conversion_example():
    result = convert_apr_periodicity("0.03582", 2, 4)
    assert result["rounded_answer"] == Decimal("0.035661")


def test_convert_apr_periodicity_matches_pdf_monthly_conversion_example():
    result = convert_apr_periodicity("0.03582", 2, 12)
    assert result["rounded_answer"] == Decimal("0.035556")


def test_convert_apr_periodicity_matches_negative_yield_example():
    result = convert_apr_periodicity("-0.00727834", 1, 2)
    assert result["rounded_answer"] == Decimal("-0.007292")


def test_current_yield_matches_pdf_brwa_example():
    result = current_yield_from_rate_and_price("3.2", "98.7")
    assert result["rounded_answer"] == Decimal("0.032421")


def test_current_yield_matches_pdf_antelas_example():
    result = current_yield_from_rate_and_price("3.2", "94")
    assert result["rounded_answer"] == Decimal("0.034043")


def test_government_equivalent_yield_matches_pdf_brwa_example():
    result = government_equivalent_yield("0.032")
    assert result["rounded_answer"] == Decimal("0.032444")


def test_g_spread_matches_pdf_russian_federation_example():
    result = g_spread_bps("0.03756", "0.0210")
    assert result["rounded_answer"] == Decimal("165.6")


def test_g_spread_matches_pdf_iif_example():
    result = g_spread_bps("0.01271", "0.00373")
    assert result["rounded_answer"] == Decimal("89.8")


def test_simple_yield_basic_formula_check():
    result = simple_yield("2", "1", "100")
    assert result["final_answer"] == Decimal("0.03")


def test_simple_yield_allows_negative_amortized_loss():
    result = simple_yield("4", "-1", "100")
    assert result["final_answer"] == Decimal("0.03")
