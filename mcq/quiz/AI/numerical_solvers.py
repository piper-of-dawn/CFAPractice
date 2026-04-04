from decimal import Decimal


def _to_decimal(value):
    return Decimal(str(value))


def _round_currency(value):
    return value.quantize(Decimal("0.01"))


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
