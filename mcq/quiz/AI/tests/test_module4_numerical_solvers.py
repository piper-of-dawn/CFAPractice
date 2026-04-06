from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from numerical_solvers import (
    cash_paid_for_income_taxes,
    cash_paid_for_interest,
    cash_paid_for_other_operating_expenses,
    cash_paid_to_employees,
    cash_paid_to_suppliers,
    cash_received_from_customers,
    cash_received_from_sale_of_equipment,
    dividends_paid,
    operating_cash_flow_direct,
    operating_cash_flow_indirect,
)


def test_cash_received_from_customers_matches_module4_example():
    result = cash_received_from_customers("100", "10")
    assert result["rounded_answer"] == Decimal("90.00")


def test_cash_paid_for_other_operating_expenses_matches_module4_example():
    result = cash_paid_for_other_operating_expenses("30", "4", "-7")
    assert result["rounded_answer"] == Decimal("41.00")


def test_cash_paid_for_interest_matches_acme_example():
    result = cash_paid_for_interest("246", "-12")
    assert result["rounded_answer"] == Decimal("258.00")


def test_cash_paid_for_income_taxes_matches_acme_example():
    result = cash_paid_for_income_taxes("1139", "5")
    assert result["rounded_answer"] == Decimal("1134.00")


def test_operating_cash_flow_indirect_matches_acme_example():
    result = operating_cash_flow_indirect(
        net_income="2210",
        depreciation_expense="1052",
        gain_on_sale_of_equipment="205",
        accounts_receivable_change="55",
        inventory_change="707",
        prepaid_expenses_change="-23",
        accounts_payable_change="263",
        salary_and_wages_payable_change="10",
        interest_payable_change="-12",
        income_tax_payable_change="5",
        other_accrued_liabilities_change="22",
    )
    assert result["rounded_answer"] == Decimal("2606.00")


def test_operating_cash_flow_direct_matches_acme_example():
    result = operating_cash_flow_direct("23543", "11900", "4113", "3532", "258", "1134")
    assert result["rounded_answer"] == Decimal("2606.00")


def test_cash_paid_to_suppliers_matches_module4_practice_problem():
    result = cash_paid_to_suppliers("80", "5", "2")
    assert result["rounded_answer"] == Decimal("83.00")


def test_cash_paid_to_employees_matches_module4_practice_problem():
    result = cash_paid_to_employees("20", "-2")
    assert result["rounded_answer"] == Decimal("22.00")


def test_dividends_paid_matches_acme_exhibit():
    result = dividends_paid("2876", "2210", "3966")
    assert result["rounded_answer"] == Decimal("1120.00")


def test_cash_received_from_sale_of_equipment_matches_module4_example():
    result = cash_received_from_sale_of_equipment("100", "10", "105", "40", "8", "46", "-2")
    assert result["rounded_answer"] == Decimal("1.00")
