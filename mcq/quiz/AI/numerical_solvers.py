from decimal import Decimal


def _to_decimal(value):
    return Decimal(str(value))


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
        "rounded_answer": total_payoff.quantize(Decimal("0.01")),
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
        "rounded_answer": ending_balance.quantize(Decimal("0.01")),
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
        "rounded_answer": margin_call.quantize(Decimal("0.01")),
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
        "rounded_answer": profit.quantize(Decimal("0.01")),
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
        "rounded_answer": threshold.quantize(Decimal("0.01")),
        "validation_checks": {
            "premium_non_negative": premium_paid >= 0,
        },
    }
