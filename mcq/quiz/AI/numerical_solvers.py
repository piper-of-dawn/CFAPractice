from decimal import Decimal


def _to_decimal(value):
    return Decimal(str(value))


def _round_currency(value):
    return value.quantize(Decimal("0.01"))


def _round_rate(value):
    return value.quantize(Decimal("0.000001"))


def future_value_lump_sum(present_value, rate_per_period, periods):
    pv = _to_decimal(present_value)
    rate = _to_decimal(rate_per_period)
    t = int(periods)
    growth_factor = (Decimal("1") + rate) ** t
    final_answer = pv * growth_factor
    return {
        "final_answer": final_answer,
        "intermediate_steps": {
            "growth_factor": growth_factor,
            "future_value": final_answer,
        },
        "units": "currency",
        "rounded_answer": _round_currency(final_answer),
        "validation_checks": {
            "periods_non_negative": t >= 0,
            "rate_greater_than_negative_one": rate > Decimal("-1"),
        },
    }


def present_value_lump_sum(future_value, rate_per_period, periods):
    fv = _to_decimal(future_value)
    rate = _to_decimal(rate_per_period)
    t = int(periods)
    discount_factor = (Decimal("1") + rate) ** (-t)
    final_answer = fv * discount_factor
    return {
        "final_answer": final_answer,
        "intermediate_steps": {
            "discount_factor": discount_factor,
            "present_value": final_answer,
        },
        "units": "currency",
        "rounded_answer": _round_currency(final_answer),
        "validation_checks": {
            "periods_non_negative": t >= 0,
            "rate_greater_than_negative_one": rate > Decimal("-1"),
        },
    }


def present_value_lump_sum_non_annual(future_value, quoted_annual_rate, compounds_per_year, years):
    fv = _to_decimal(future_value)
    quoted_rate = _to_decimal(quoted_annual_rate)
    m = int(compounds_per_year)
    n = int(years)
    periodic_rate = quoted_rate / Decimal(m)
    total_periods = m * n
    discount_factor = (Decimal("1") + periodic_rate) ** (-total_periods)
    final_answer = fv * discount_factor
    return {
        "final_answer": final_answer,
        "intermediate_steps": {
            "periodic_rate": periodic_rate,
            "total_periods": total_periods,
            "discount_factor": discount_factor,
            "present_value": final_answer,
        },
        "units": "currency",
        "rounded_answer": _round_currency(final_answer),
        "validation_checks": {
            "compounds_per_year_positive": m > 0,
            "years_non_negative": n >= 0,
            "quoted_rate_greater_than_negative_compounds": quoted_rate > Decimal(-m),
        },
    }


def implied_rate_lump_sum(present_value, future_value, periods):
    pv = _to_decimal(present_value)
    fv = _to_decimal(future_value)
    t = int(periods)
    ratio = fv / pv
    exponent = Decimal("1") / Decimal(t)
    rate = ratio.__pow__(exponent) - Decimal("1")
    return {
        "final_answer": rate,
        "intermediate_steps": {
            "future_value_to_present_value_ratio": ratio,
            "implied_rate": rate,
        },
        "units": "rate per period",
        "rounded_answer": rate.quantize(Decimal("0.0001")),
        "validation_checks": {
            "present_value_positive": pv > 0,
            "future_value_positive": fv > 0,
            "periods_positive": t > 0,
        },
    }


def forward_payoff(contract_size, forward_price, spot_at_maturity):
    size = _to_decimal(contract_size)
    fwd = _to_decimal(forward_price)
    spot = _to_decimal(spot_at_maturity)
    payoff_per_unit = spot - fwd
    total_payoff = payoff_per_unit * size
    return {
        "final_answer": total_payoff,
        "intermediate_steps": {
            "payoff_per_unit": payoff_per_unit,
            "total_payoff": total_payoff,
        },
        "units": "currency",
        "rounded_answer": _round_currency(total_payoff),
        "validation_checks": {
            "contract_size_non_negative": size >= 0,
        },
    }


def futures_daily_mtm(contract_size, prior_futures_price, current_futures_price, starting_margin_balance):
    size = _to_decimal(contract_size)
    prior_price = _to_decimal(prior_futures_price)
    current_price = _to_decimal(current_futures_price)
    starting_balance = _to_decimal(starting_margin_balance)
    day_gain_loss = (current_price - prior_price) * size
    ending_balance = starting_balance + day_gain_loss
    return {
        "final_answer": ending_balance,
        "intermediate_steps": {
            "day_gain_loss": day_gain_loss,
            "ending_balance": ending_balance,
        },
        "units": "currency",
        "rounded_answer": _round_currency(ending_balance),
        "validation_checks": {
            "contract_size_non_negative": size >= 0,
        },
    }


def futures_margin_call(initial_margin, maintenance_margin, ending_balance_before_call):
    initial = _to_decimal(initial_margin)
    maintenance = _to_decimal(maintenance_margin)
    ending_balance = _to_decimal(ending_balance_before_call)
    margin_call = Decimal("0")
    if ending_balance < maintenance:
        margin_call = initial - ending_balance
    return {
        "final_answer": margin_call,
        "intermediate_steps": {
            "ending_balance_before_call": ending_balance,
            "maintenance_margin": maintenance,
            "initial_margin": initial,
            "margin_call": margin_call,
        },
        "units": "currency",
        "rounded_answer": _round_currency(margin_call),
        "validation_checks": {
            "initial_margin_at_least_maintenance": initial >= maintenance,
        },
    }


def long_call_profit(spot_at_expiry, exercise_price, premium):
    spot = _to_decimal(spot_at_expiry)
    exercise = _to_decimal(exercise_price)
    premium_paid = _to_decimal(premium)
    payoff = max(Decimal("0"), spot - exercise)
    profit = payoff - premium_paid
    return {
        "final_answer": profit,
        "intermediate_steps": {
            "payoff": payoff,
            "profit": profit,
        },
        "units": "currency per unit",
        "rounded_answer": _round_currency(profit),
        "validation_checks": {
            "premium_non_negative": premium_paid >= 0,
        },
    }


def long_put_profit_threshold(exercise_price, premium):
    exercise = _to_decimal(exercise_price)
    premium_paid = _to_decimal(premium)
    threshold = exercise - premium_paid
    return {
        "final_answer": threshold,
        "intermediate_steps": {
            "exercise_price_minus_premium": threshold,
        },
        "units": "currency per unit",
        "rounded_answer": _round_currency(threshold),
        "validation_checks": {
            "premium_non_negative": premium_paid >= 0,
        },
    }


def annual_yield_from_periodic_rate(rate_per_period, periods_per_year):
    periodic_rate = _to_decimal(rate_per_period)
    periodicity = _to_decimal(periods_per_year)
    annual_yield = periodic_rate * periodicity
    return {
        "final_answer": annual_yield,
        "intermediate_steps": {
            "rate_per_period": periodic_rate,
            "periods_per_year": periodicity,
            "annual_yield": annual_yield,
        },
        "units": "annual rate",
        "rounded_answer": _round_rate(annual_yield),
        "validation_checks": {
            "periods_per_year_positive": periodicity > 0,
        },
    }


def convert_apr_periodicity(apr_m, periods_per_year_m, periods_per_year_n):
    apr_source = _to_decimal(apr_m)
    m = _to_decimal(periods_per_year_m)
    n = _to_decimal(periods_per_year_n)
    effective_annual_rate = (Decimal("1") + (apr_source / m)) ** m - Decimal("1")
    apr_target = n * ((Decimal("1") + effective_annual_rate) ** (Decimal("1") / n) - Decimal("1"))
    return {
        "final_answer": apr_target,
        "intermediate_steps": {
            "source_apr": apr_source,
            "source_periodicity": m,
            "target_periodicity": n,
            "effective_annual_rate": effective_annual_rate,
            "target_apr": apr_target,
        },
        "units": "annual rate",
        "rounded_answer": _round_rate(apr_target),
        "validation_checks": {
            "source_periodicity_positive": m > 0,
            "target_periodicity_positive": n > 0,
            "apr_above_negative_source_periodicity": apr_source > -m,
        },
    }


def current_yield_from_rate_and_price(annual_coupon_rate_percent_of_par, flat_price_percent_of_par):
    annual_coupon_rate = _to_decimal(annual_coupon_rate_percent_of_par)
    flat_price = _to_decimal(flat_price_percent_of_par)
    current_yield = annual_coupon_rate / flat_price
    return {
        "final_answer": current_yield,
        "intermediate_steps": {
            "annual_coupon_rate_percent_of_par": annual_coupon_rate,
            "flat_price_percent_of_par": flat_price,
            "current_yield": current_yield,
        },
        "units": "annual rate",
        "rounded_answer": _round_rate(current_yield),
        "validation_checks": {
            "flat_price_positive": flat_price > 0,
        },
    }


def government_equivalent_yield(corporate_yield_30_360):
    corporate_yield = _to_decimal(corporate_yield_30_360)
    act_act_yield = corporate_yield * Decimal("365") / Decimal("360")
    return {
        "final_answer": act_act_yield,
        "intermediate_steps": {
            "corporate_yield_30_360": corporate_yield,
            "conversion_factor_365_over_360": Decimal("365") / Decimal("360"),
            "government_equivalent_yield": act_act_yield,
        },
        "units": "annual rate",
        "rounded_answer": _round_rate(act_act_yield),
        "validation_checks": {
            "yield_non_negative": corporate_yield >= 0,
        },
    }


def simple_yield(annual_coupon_amount, straight_line_amortized_gain_or_loss, flat_price):
    annual_coupon = _to_decimal(annual_coupon_amount)
    amortized_gain_or_loss = _to_decimal(straight_line_amortized_gain_or_loss)
    price = _to_decimal(flat_price)
    result = (annual_coupon + amortized_gain_or_loss) / price
    return {
        "final_answer": result,
        "intermediate_steps": {
            "annual_coupon_amount": annual_coupon,
            "straight_line_amortized_gain_or_loss": amortized_gain_or_loss,
            "flat_price": price,
            "simple_yield": result,
        },
        "units": "annual rate",
        "rounded_answer": _round_rate(result),
        "validation_checks": {
            "flat_price_positive": price > 0,
        },
    }


def g_spread_bps(bond_yield, benchmark_yield):
    bond = _to_decimal(bond_yield)
    benchmark = _to_decimal(benchmark_yield)
    spread = bond - benchmark
    spread_bps = spread * Decimal("10000")
    return {
        "final_answer": spread_bps,
        "intermediate_steps": {
            "bond_yield": bond,
            "benchmark_yield": benchmark,
            "spread_decimal": spread,
            "spread_bps": spread_bps,
        },
        "units": "basis points",
        "rounded_answer": spread_bps.quantize(Decimal("0.1")),
        "validation_checks": {
            "inputs_present": True,
        },
    }


def bond_price_coupon_date(periodic_coupon_amount, periodic_discount_rate, periods_to_maturity, face_value):
    coupon = _to_decimal(periodic_coupon_amount)
    rate = _to_decimal(periodic_discount_rate)
    periods = int(periods_to_maturity)
    face = _to_decimal(face_value)
    present_value = Decimal("0")
    for t in range(1, periods + 1):
        cash_flow = coupon
        if t == periods:
            cash_flow += face
        present_value += cash_flow / ((Decimal("1") + rate) ** t)
    return {
        "final_answer": present_value,
        "intermediate_steps": {
            "periodic_coupon_amount": coupon,
            "periodic_discount_rate": rate,
            "periods_to_maturity": periods,
            "face_value": face,
            "price": present_value,
        },
        "units": "price per 100 of par value",
        "rounded_answer": present_value.quantize(Decimal("0.001")),
        "validation_checks": {
            "periods_positive": periods > 0,
            "rate_greater_than_negative_one": rate > Decimal("-1"),
        },
    }


def accrued_interest(coupon_payment_per_period, days_elapsed, days_in_period):
    coupon = _to_decimal(coupon_payment_per_period)
    t = _to_decimal(days_elapsed)
    total_days = _to_decimal(days_in_period)
    accrued = (t / total_days) * coupon
    return {
        "final_answer": accrued,
        "intermediate_steps": {
            "coupon_payment_per_period": coupon,
            "days_elapsed": t,
            "days_in_period": total_days,
            "fraction_of_period_elapsed": t / total_days,
            "accrued_interest": accrued,
        },
        "units": "price per 100 of par value",
        "rounded_answer": accrued.quantize(Decimal("0.001")),
        "validation_checks": {
            "days_in_period_positive": total_days > 0,
            "days_elapsed_non_negative": t >= 0,
            "days_elapsed_not_more_than_period": t <= total_days,
        },
    }


def full_price_between_coupons(price_at_start_of_period, periodic_discount_rate, days_elapsed, days_in_period):
    pv = _to_decimal(price_at_start_of_period)
    rate = _to_decimal(periodic_discount_rate)
    t = _to_decimal(days_elapsed)
    total_days = _to_decimal(days_in_period)
    exponent = t / total_days
    full_price = pv * ((Decimal("1") + rate) ** exponent)
    return {
        "final_answer": full_price,
        "intermediate_steps": {
            "price_at_start_of_period": pv,
            "periodic_discount_rate": rate,
            "days_elapsed": t,
            "days_in_period": total_days,
            "exponent_t_over_T": exponent,
            "full_price": full_price,
        },
        "units": "price per 100 of par value",
        "rounded_answer": full_price.quantize(Decimal("0.001")),
        "validation_checks": {
            "days_in_period_positive": total_days > 0,
            "days_elapsed_non_negative": t >= 0,
            "rate_greater_than_negative_one": rate > Decimal("-1"),
        },
    }


def flat_price_from_full_price(full_price_value, accrued_interest_value):
    full_price = _to_decimal(full_price_value)
    accrued = _to_decimal(accrued_interest_value)
    flat_price = full_price - accrued
    return {
        "final_answer": flat_price,
        "intermediate_steps": {
            "full_price": full_price,
            "accrued_interest": accrued,
            "flat_price": flat_price,
        },
        "units": "price per 100 of par value",
        "rounded_answer": flat_price.quantize(Decimal("0.001")),
        "validation_checks": {
            "full_price_at_least_accrued_interest": full_price >= accrued,
        },
    }


def interpolated_yield(lower_maturity, upper_maturity, target_maturity, lower_yield, upper_yield):
    lower_m = _to_decimal(lower_maturity)
    upper_m = _to_decimal(upper_maturity)
    target_m = _to_decimal(target_maturity)
    lower_y = _to_decimal(lower_yield)
    upper_y = _to_decimal(upper_yield)
    weight = (target_m - lower_m) / (upper_m - lower_m)
    interpolated = lower_y + weight * (upper_y - lower_y)
    return {
        "final_answer": interpolated,
        "intermediate_steps": {
            "lower_maturity": lower_m,
            "upper_maturity": upper_m,
            "target_maturity": target_m,
            "lower_yield": lower_y,
            "upper_yield": upper_y,
            "interpolation_weight": weight,
            "interpolated_yield": interpolated,
        },
        "units": "annual yield",
        "rounded_answer": _round_rate(interpolated),
        "validation_checks": {
            "upper_maturity_greater_than_lower": upper_m > lower_m,
            "target_between_bounds": target_m >= lower_m and target_m <= upper_m,
        },
    }


def cash_received_from_customers(revenue, accounts_receivable_change):
    sales = _to_decimal(revenue)
    ar_change = _to_decimal(accounts_receivable_change)
    cash_received = sales - ar_change
    return {
        "final_answer": cash_received,
        "intermediate_steps": {
            "revenue": sales,
            "accounts_receivable_change": ar_change,
            "cash_received_from_customers": cash_received,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_received),
        "validation_checks": {
            "revenue_non_negative": sales >= 0,
        },
    }


def purchases_from_suppliers(cost_of_goods_sold, inventory_change):
    cogs = _to_decimal(cost_of_goods_sold)
    inv_change = _to_decimal(inventory_change)
    purchases = cogs + inv_change
    return {
        "final_answer": purchases,
        "intermediate_steps": {
            "cost_of_goods_sold": cogs,
            "inventory_change": inv_change,
            "purchases_from_suppliers": purchases,
        },
        "units": "currency",
        "rounded_answer": _round_currency(purchases),
        "validation_checks": {
            "cost_of_goods_sold_non_negative": cogs >= 0,
        },
    }


def cash_paid_to_suppliers(cost_of_goods_sold, inventory_change, accounts_payable_change):
    cogs = _to_decimal(cost_of_goods_sold)
    inv_change = _to_decimal(inventory_change)
    ap_change = _to_decimal(accounts_payable_change)
    purchases = cogs + inv_change
    cash_paid = purchases - ap_change
    return {
        "final_answer": cash_paid,
        "intermediate_steps": {
            "cost_of_goods_sold": cogs,
            "inventory_change": inv_change,
            "purchases_from_suppliers": purchases,
            "accounts_payable_change": ap_change,
            "cash_paid_to_suppliers": cash_paid,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_paid),
        "validation_checks": {
            "cost_of_goods_sold_non_negative": cogs >= 0,
        },
    }


def cash_paid_to_employees(salary_and_wages_expense, salary_and_wages_payable_change):
    expense = _to_decimal(salary_and_wages_expense)
    payable_change = _to_decimal(salary_and_wages_payable_change)
    cash_paid = expense - payable_change
    return {
        "final_answer": cash_paid,
        "intermediate_steps": {
            "salary_and_wages_expense": expense,
            "salary_and_wages_payable_change": payable_change,
            "cash_paid_to_employees": cash_paid,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_paid),
        "validation_checks": {
            "salary_and_wages_expense_non_negative": expense >= 0,
        },
    }


def cash_paid_for_other_operating_expenses(
    other_operating_expenses,
    prepaid_expenses_change,
    other_accrued_liabilities_change,
):
    expense = _to_decimal(other_operating_expenses)
    prepaid_change = _to_decimal(prepaid_expenses_change)
    accrued_change = _to_decimal(other_accrued_liabilities_change)
    cash_paid = expense + prepaid_change - accrued_change
    return {
        "final_answer": cash_paid,
        "intermediate_steps": {
            "other_operating_expenses": expense,
            "prepaid_expenses_change": prepaid_change,
            "other_accrued_liabilities_change": accrued_change,
            "cash_paid_for_other_operating_expenses": cash_paid,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_paid),
        "validation_checks": {
            "other_operating_expenses_non_negative": expense >= 0,
        },
    }


def cash_paid_for_interest(interest_expense, interest_payable_change):
    expense = _to_decimal(interest_expense)
    payable_change = _to_decimal(interest_payable_change)
    cash_paid = expense - payable_change
    return {
        "final_answer": cash_paid,
        "intermediate_steps": {
            "interest_expense": expense,
            "interest_payable_change": payable_change,
            "cash_paid_for_interest": cash_paid,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_paid),
        "validation_checks": {
            "interest_expense_non_negative": expense >= 0,
        },
    }


def cash_paid_for_income_taxes(
    income_tax_expense,
    income_tax_payable_change="0",
    taxes_receivable_change="0",
    deferred_tax_assets_change="0",
    deferred_tax_liabilities_change="0",
):
    expense = _to_decimal(income_tax_expense)
    payable_change = _to_decimal(income_tax_payable_change)
    receivable_change = _to_decimal(taxes_receivable_change)
    dta_change = _to_decimal(deferred_tax_assets_change)
    dtl_change = _to_decimal(deferred_tax_liabilities_change)
    cash_paid = expense - payable_change + receivable_change + dta_change - dtl_change
    return {
        "final_answer": cash_paid,
        "intermediate_steps": {
            "income_tax_expense": expense,
            "income_tax_payable_change": payable_change,
            "taxes_receivable_change": receivable_change,
            "deferred_tax_assets_change": dta_change,
            "deferred_tax_liabilities_change": dtl_change,
            "cash_paid_for_income_taxes": cash_paid,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_paid),
        "validation_checks": {
            "income_tax_expense_non_negative": expense >= 0,
        },
    }


def operating_cash_flow_direct(
    cash_received_from_customers_value,
    cash_paid_to_suppliers_value,
    cash_paid_to_employees_value,
    cash_paid_for_other_operating_expenses_value,
    cash_paid_for_interest_value,
    cash_paid_for_income_taxes_value,
):
    cash_received = _to_decimal(cash_received_from_customers_value)
    cash_suppliers = _to_decimal(cash_paid_to_suppliers_value)
    cash_employees = _to_decimal(cash_paid_to_employees_value)
    cash_other = _to_decimal(cash_paid_for_other_operating_expenses_value)
    cash_interest = _to_decimal(cash_paid_for_interest_value)
    cash_taxes = _to_decimal(cash_paid_for_income_taxes_value)
    cfo = cash_received - cash_suppliers - cash_employees - cash_other - cash_interest - cash_taxes
    return {
        "final_answer": cfo,
        "intermediate_steps": {
            "cash_received_from_customers": cash_received,
            "cash_paid_to_suppliers": cash_suppliers,
            "cash_paid_to_employees": cash_employees,
            "cash_paid_for_other_operating_expenses": cash_other,
            "cash_paid_for_interest": cash_interest,
            "cash_paid_for_income_taxes": cash_taxes,
            "operating_cash_flow": cfo,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cfo),
        "validation_checks": {
            "cash_received_non_negative": cash_received >= 0,
        },
    }


def operating_cash_flow_indirect(
    net_income,
    depreciation_expense="0",
    gain_on_sale_of_equipment="0",
    loss_on_sale_of_equipment="0",
    accounts_receivable_change="0",
    inventory_change="0",
    prepaid_expenses_change="0",
    accounts_payable_change="0",
    salary_and_wages_payable_change="0",
    interest_payable_change="0",
    income_tax_payable_change="0",
    other_accrued_liabilities_change="0",
):
    ni = _to_decimal(net_income)
    depreciation = _to_decimal(depreciation_expense)
    gain = _to_decimal(gain_on_sale_of_equipment)
    loss = _to_decimal(loss_on_sale_of_equipment)
    ar_change = _to_decimal(accounts_receivable_change)
    inv_change = _to_decimal(inventory_change)
    prepaid_change = _to_decimal(prepaid_expenses_change)
    ap_change = _to_decimal(accounts_payable_change)
    wages_payable_change = _to_decimal(salary_and_wages_payable_change)
    interest_payable = _to_decimal(interest_payable_change)
    tax_payable = _to_decimal(income_tax_payable_change)
    other_accrued = _to_decimal(other_accrued_liabilities_change)
    cfo = (
        ni
        + depreciation
        - gain
        + loss
        - ar_change
        - inv_change
        - prepaid_change
        + ap_change
        + wages_payable_change
        + interest_payable
        + tax_payable
        + other_accrued
    )
    return {
        "final_answer": cfo,
        "intermediate_steps": {
            "net_income": ni,
            "depreciation_expense": depreciation,
            "gain_on_sale_of_equipment": gain,
            "loss_on_sale_of_equipment": loss,
            "accounts_receivable_change": ar_change,
            "inventory_change": inv_change,
            "prepaid_expenses_change": prepaid_change,
            "accounts_payable_change": ap_change,
            "salary_and_wages_payable_change": wages_payable_change,
            "interest_payable_change": interest_payable,
            "income_tax_payable_change": tax_payable,
            "other_accrued_liabilities_change": other_accrued,
            "operating_cash_flow": cfo,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cfo),
        "validation_checks": {
            "net_income_numeric": True,
        },
    }


def dividends_paid(beginning_retained_earnings, net_income, ending_retained_earnings):
    beginning = _to_decimal(beginning_retained_earnings)
    income = _to_decimal(net_income)
    ending = _to_decimal(ending_retained_earnings)
    dividends = beginning + income - ending
    return {
        "final_answer": dividends,
        "intermediate_steps": {
            "beginning_retained_earnings": beginning,
            "net_income": income,
            "ending_retained_earnings": ending,
            "dividends_paid": dividends,
        },
        "units": "currency",
        "rounded_answer": _round_currency(dividends),
        "validation_checks": {
            "all_inputs_numeric": True,
        },
    }


def cash_received_from_sale_of_equipment(
    beginning_equipment,
    equipment_purchased,
    ending_equipment,
    beginning_accumulated_depreciation,
    depreciation_expense,
    ending_accumulated_depreciation,
    gain_or_loss_on_sale,
):
    beginning_eq = _to_decimal(beginning_equipment)
    purchased = _to_decimal(equipment_purchased)
    ending_eq = _to_decimal(ending_equipment)
    beginning_ad = _to_decimal(beginning_accumulated_depreciation)
    depreciation = _to_decimal(depreciation_expense)
    ending_ad = _to_decimal(ending_accumulated_depreciation)
    gain_or_loss = _to_decimal(gain_or_loss_on_sale)
    historical_cost_sold = beginning_eq + purchased - ending_eq
    accumulated_depreciation_sold = beginning_ad + depreciation - ending_ad
    book_value_sold = historical_cost_sold - accumulated_depreciation_sold
    cash_received = book_value_sold + gain_or_loss
    return {
        "final_answer": cash_received,
        "intermediate_steps": {
            "historical_cost_of_equipment_sold": historical_cost_sold,
            "accumulated_depreciation_on_equipment_sold": accumulated_depreciation_sold,
            "book_value_of_equipment_sold": book_value_sold,
            "gain_or_loss_on_sale": gain_or_loss,
            "cash_received_from_sale_of_equipment": cash_received,
        },
        "units": "currency",
        "rounded_answer": _round_currency(cash_received),
        "validation_checks": {
            "historical_cost_sold_non_negative": historical_cost_sold >= 0,
            "accumulated_depreciation_sold_non_negative": accumulated_depreciation_sold >= 0,
        },
    }


def _round_stat(value, places="0.0001"):
    return value.quantize(Decimal(places))


def regression_slope_from_deviation_sums(sum_cross_deviations, sum_x_squared_deviations):
    numerator = _to_decimal(sum_cross_deviations)
    denominator = _to_decimal(sum_x_squared_deviations)
    slope = numerator / denominator
    return {
        "final_answer": slope,
        "intermediate_steps": {
            "sum_cross_deviations": numerator,
            "sum_x_squared_deviations": denominator,
            "slope": slope,
        },
        "units": "slope coefficient",
        "rounded_answer": _round_stat(slope),
        "validation_checks": {
            "x_variation_non_zero": denominator != 0,
        },
    }


def regression_intercept_from_means(y_mean, slope, x_mean):
    y_bar = _to_decimal(y_mean)
    beta_1 = _to_decimal(slope)
    x_bar = _to_decimal(x_mean)
    intercept = y_bar - (beta_1 * x_bar)
    return {
        "final_answer": intercept,
        "intermediate_steps": {
            "y_mean": y_bar,
            "slope": beta_1,
            "x_mean": x_bar,
            "intercept": intercept,
        },
        "units": "intercept coefficient",
        "rounded_answer": _round_stat(intercept),
        "validation_checks": {
            "inputs_numeric": True,
        },
    }


def correlation_from_covariance_and_standard_deviations(covariance_xy, standard_deviation_y, standard_deviation_x):
    covariance = _to_decimal(covariance_xy)
    s_y = _to_decimal(standard_deviation_y)
    s_x = _to_decimal(standard_deviation_x)
    correlation = covariance / (s_y * s_x)
    return {
        "final_answer": correlation,
        "intermediate_steps": {
            "covariance_xy": covariance,
            "standard_deviation_y": s_y,
            "standard_deviation_x": s_x,
            "correlation": correlation,
        },
        "units": "correlation",
        "rounded_answer": _round_stat(correlation),
        "validation_checks": {
            "standard_deviations_positive": s_y > 0 and s_x > 0,
        },
    }


def coefficient_of_determination(ssr, sst):
    regression_sum_squares = _to_decimal(ssr)
    total_sum_squares = _to_decimal(sst)
    r_squared = regression_sum_squares / total_sum_squares
    return {
        "final_answer": r_squared,
        "intermediate_steps": {
            "sum_squares_regression": regression_sum_squares,
            "sum_squares_total": total_sum_squares,
            "r_squared": r_squared,
        },
        "units": "coefficient of determination",
        "rounded_answer": _round_stat(r_squared),
        "validation_checks": {
            "sst_positive": total_sum_squares > 0,
        },
    }


def mean_square_error(sse, observations, independent_variables=1):
    error_sum_squares = _to_decimal(sse)
    n = int(observations)
    k = int(independent_variables)
    denominator = n - k - 1
    mse = error_sum_squares / Decimal(denominator)
    return {
        "final_answer": mse,
        "intermediate_steps": {
            "sum_squares_error": error_sum_squares,
            "observations": Decimal(n),
            "independent_variables": Decimal(k),
            "degrees_of_freedom_error": Decimal(denominator),
            "mean_square_error": mse,
        },
        "units": "mean square error",
        "rounded_answer": _round_stat(mse),
        "validation_checks": {
            "error_degrees_of_freedom_positive": denominator > 0,
        },
    }


def f_statistic_from_mean_squares(msr, mse):
    mean_square_regression = _to_decimal(msr)
    mean_square_err = _to_decimal(mse)
    f_stat = mean_square_regression / mean_square_err
    return {
        "final_answer": f_stat,
        "intermediate_steps": {
            "mean_square_regression": mean_square_regression,
            "mean_square_error": mean_square_err,
            "f_statistic": f_stat,
        },
        "units": "F-statistic",
        "rounded_answer": _round_stat(f_stat),
        "validation_checks": {
            "mse_positive": mean_square_err > 0,
        },
    }


def standard_error_of_estimate_from_mse(mse):
    mean_square_err = _to_decimal(mse)
    se = mean_square_err.sqrt()
    return {
        "final_answer": se,
        "intermediate_steps": {
            "mean_square_error": mean_square_err,
            "standard_error_of_estimate": se,
        },
        "units": "standard error of estimate",
        "rounded_answer": _round_stat(se),
        "validation_checks": {
            "mse_non_negative": mean_square_err >= 0,
        },
    }


def sample_variance_from_sst(sst, observations):
    total_sum_squares = _to_decimal(sst)
    n = int(observations)
    variance = total_sum_squares / Decimal(n - 1)
    return {
        "final_answer": variance,
        "intermediate_steps": {
            "sum_squares_total": total_sum_squares,
            "observations": Decimal(n),
            "degrees_of_freedom_total": Decimal(n - 1),
            "sample_variance": variance,
        },
        "units": "sample variance",
        "rounded_answer": _round_stat(variance),
        "validation_checks": {
            "observations_greater_than_one": n > 1,
        },
    }


def standard_error_of_slope(standard_error_estimate, sum_x_squared_deviations):
    se = _to_decimal(standard_error_estimate)
    x_variation = _to_decimal(sum_x_squared_deviations)
    slope_se = se / x_variation.sqrt()
    return {
        "final_answer": slope_se,
        "intermediate_steps": {
            "standard_error_of_estimate": se,
            "sum_x_squared_deviations": x_variation,
            "standard_error_of_slope": slope_se,
        },
        "units": "standard error of slope",
        "rounded_answer": _round_stat(slope_se, "0.000001"),
        "validation_checks": {
            "x_variation_positive": x_variation > 0,
        },
    }


def t_statistic_for_slope(estimated_slope, hypothesized_slope, standard_error_slope):
    beta_hat = _to_decimal(estimated_slope)
    beta_hyp = _to_decimal(hypothesized_slope)
    slope_se = _to_decimal(standard_error_slope)
    t_value = (beta_hat - beta_hyp) / slope_se
    return {
        "final_answer": t_value,
        "intermediate_steps": {
            "estimated_slope": beta_hat,
            "hypothesized_slope": beta_hyp,
            "standard_error_of_slope": slope_se,
            "t_statistic": t_value,
        },
        "units": "t-statistic",
        "rounded_answer": _round_stat(t_value, "0.00001"),
        "validation_checks": {
            "standard_error_slope_positive": slope_se > 0,
        },
    }


def t_statistic_for_correlation(correlation, observations):
    r_value = _to_decimal(correlation)
    n = int(observations)
    numerator = r_value * Decimal(n - 2).sqrt()
    denominator = (Decimal("1") - (r_value * r_value)).sqrt()
    t_value = numerator / denominator
    return {
        "final_answer": t_value,
        "intermediate_steps": {
            "correlation": r_value,
            "observations": Decimal(n),
            "numerator": numerator,
            "denominator": denominator,
            "t_statistic": t_value,
        },
        "units": "t-statistic",
        "rounded_answer": _round_stat(t_value, "0.00001"),
        "validation_checks": {
            "observations_greater_than_two": n > 2,
            "correlation_magnitude_below_one": abs(r_value) < 1,
        },
    }


def standard_error_of_intercept(standard_error_estimate, observations, x_mean, sum_x_squared_deviations):
    se = _to_decimal(standard_error_estimate)
    n = int(observations)
    x_bar = _to_decimal(x_mean)
    x_variation = _to_decimal(sum_x_squared_deviations)
    term = (Decimal("1") / Decimal(n)) + ((x_bar * x_bar) / x_variation)
    intercept_se = se * term.sqrt()
    return {
        "final_answer": intercept_se,
        "intermediate_steps": {
            "standard_error_of_estimate": se,
            "observations": Decimal(n),
            "x_mean": x_bar,
            "sum_x_squared_deviations": x_variation,
            "scaling_term": term,
            "standard_error_of_intercept": intercept_se,
        },
        "units": "standard error of intercept",
        "rounded_answer": _round_stat(intercept_se, "0.00001"),
        "validation_checks": {
            "observations_positive": n > 0,
            "x_variation_positive": x_variation > 0,
        },
    }


def t_statistic_for_intercept(estimated_intercept, hypothesized_intercept, standard_error_intercept):
    intercept_hat = _to_decimal(estimated_intercept)
    intercept_hyp = _to_decimal(hypothesized_intercept)
    intercept_se = _to_decimal(standard_error_intercept)
    t_value = (intercept_hat - intercept_hyp) / intercept_se
    return {
        "final_answer": t_value,
        "intermediate_steps": {
            "estimated_intercept": intercept_hat,
            "hypothesized_intercept": intercept_hyp,
            "standard_error_of_intercept": intercept_se,
            "t_statistic": t_value,
        },
        "units": "t-statistic",
        "rounded_answer": _round_stat(t_value, "0.0001"),
        "validation_checks": {
            "standard_error_intercept_positive": intercept_se > 0,
        },
    }


def predicted_value_simple_linear_regression(intercept, slope, forecast_x):
    beta_0 = _to_decimal(intercept)
    beta_1 = _to_decimal(slope)
    x_forecast = _to_decimal(forecast_x)
    predicted = beta_0 + (beta_1 * x_forecast)
    return {
        "final_answer": predicted,
        "intermediate_steps": {
            "intercept": beta_0,
            "slope": beta_1,
            "forecast_x": x_forecast,
            "predicted_y": predicted,
        },
        "units": "predicted dependent variable",
        "rounded_answer": _round_stat(predicted, "0.0001"),
        "validation_checks": {
            "inputs_numeric": True,
        },
    }


def sum_x_squared_deviations_from_sample_variance(sample_variance_x, observations):
    variance_x = _to_decimal(sample_variance_x)
    n = int(observations)
    sum_sq_dev = variance_x * Decimal(n - 1)
    return {
        "final_answer": sum_sq_dev,
        "intermediate_steps": {
            "sample_variance_x": variance_x,
            "observations": Decimal(n),
            "sum_x_squared_deviations": sum_sq_dev,
        },
        "units": "sum of squared deviations of x",
        "rounded_answer": _round_stat(sum_sq_dev),
        "validation_checks": {
            "observations_greater_than_one": n > 1,
        },
    }


def standard_error_of_forecast(standard_error_estimate, observations, forecast_x, x_mean, sum_x_squared_deviations):
    se = _to_decimal(standard_error_estimate)
    n = int(observations)
    x_forecast = _to_decimal(forecast_x)
    x_bar = _to_decimal(x_mean)
    x_variation = _to_decimal(sum_x_squared_deviations)
    term = Decimal("1") + (Decimal("1") / Decimal(n)) + (((x_forecast - x_bar) ** 2) / x_variation)
    forecast_se = se * term.sqrt()
    return {
        "final_answer": forecast_se,
        "intermediate_steps": {
            "standard_error_of_estimate": se,
            "observations": Decimal(n),
            "forecast_x": x_forecast,
            "x_mean": x_bar,
            "sum_x_squared_deviations": x_variation,
            "scaling_term": term,
            "standard_error_of_forecast": forecast_se,
        },
        "units": "standard error of forecast",
        "rounded_answer": _round_stat(forecast_se, "0.0001"),
        "validation_checks": {
            "observations_positive": n > 0,
            "x_variation_positive": x_variation > 0,
        },
    }


def prediction_interval(predicted_value, critical_t, standard_error_forecast):
    forecast = _to_decimal(predicted_value)
    t_critical = _to_decimal(critical_t)
    forecast_se = _to_decimal(standard_error_forecast)
    half_width = t_critical * forecast_se
    lower_bound = forecast - half_width
    upper_bound = forecast + half_width
    return {
        "final_answer": {
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        },
        "intermediate_steps": {
            "predicted_value": forecast,
            "critical_t": t_critical,
            "standard_error_of_forecast": forecast_se,
            "half_width": half_width,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        },
        "units": "prediction interval",
        "rounded_answer": {
            "lower_bound": _round_stat(lower_bound, "0.0001"),
            "upper_bound": _round_stat(upper_bound, "0.0001"),
        },
        "validation_checks": {
            "critical_t_non_negative": t_critical >= 0,
            "standard_error_forecast_non_negative": forecast_se >= 0,
        },
    }


def level_forecast_from_log_lin(intercept, slope, forecast_x):
    beta_0 = _to_decimal(intercept)
    beta_1 = _to_decimal(slope)
    x_forecast = _to_decimal(forecast_x)
    ln_y = beta_0 + (beta_1 * x_forecast)
    y_level = ln_y.exp()
    return {
        "final_answer": y_level,
        "intermediate_steps": {
            "intercept": beta_0,
            "slope": beta_1,
            "forecast_x": x_forecast,
            "predicted_ln_y": ln_y,
            "predicted_y_level": y_level,
        },
        "units": "predicted dependent variable level",
        "rounded_answer": _round_stat(y_level, "0.000001"),
        "validation_checks": {
            "inputs_numeric": True,
        },
    }
