from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from numerical_solvers import (
    coefficient_of_determination,
    correlation_from_covariance_and_standard_deviations,
    f_statistic_from_mean_squares,
    level_forecast_from_log_lin,
    mean_square_error,
    predicted_value_simple_linear_regression,
    prediction_interval,
    regression_intercept_from_means,
    regression_slope_from_deviation_sums,
    sample_variance_from_sst,
    standard_error_of_estimate_from_mse,
    standard_error_of_forecast,
    standard_error_of_intercept,
    standard_error_of_slope,
    sum_x_squared_deviations_from_sample_variance,
    t_statistic_for_correlation,
    t_statistic_for_intercept,
    t_statistic_for_slope,
)


def test_regression_slope_matches_roa_capex_example():
    result = regression_slope_from_deviation_sums("153.30", "122.64")
    assert result["rounded_answer"] == Decimal("1.2500")


def test_regression_intercept_matches_roa_capex_example():
    result = regression_intercept_from_means("12.5", "1.25", "6.1")
    assert result["rounded_answer"] == Decimal("4.8750")


def test_correlation_matches_roa_capex_example():
    result = correlation_from_covariance_and_standard_deviations("30.66", "6.9210", "4.9526")
    assert result["rounded_answer"] == Decimal("0.8945")


def test_slope_t_statistic_matches_roa_test_against_zero():
    slope_se = standard_error_of_slope("3.459588", "122.640")
    result = t_statistic_for_slope("1.25", "0", slope_se["final_answer"])
    assert result["rounded_answer"] == Decimal("4.00131")


def test_correlation_t_statistic_matches_roa_example():
    result = t_statistic_for_correlation("0.8945", 6)
    assert result["rounded_answer"] == Decimal("4.00163")


def test_intercept_t_statistic_matches_roa_example():
    intercept_se = standard_error_of_intercept("3.4596", 6, "6.1", "122.64")
    result = t_statistic_for_intercept("4.875", "3.0", intercept_se["final_answer"])
    assert result["rounded_answer"] == Decimal("0.7905")


def test_r_squared_matches_roa_example():
    result = coefficient_of_determination("191.625", "239.50")
    assert result["rounded_answer"] == Decimal("0.8001")


def test_f_statistic_matches_question_set_exhibit_36():
    result = f_statistic_from_mean_squares("576.1485", "19.1180")
    assert result["rounded_answer"] == Decimal("30.1364")


def test_sample_variance_matches_exhibit_37():
    result = sample_variance_from_sst("95.2", 5)
    assert result["rounded_answer"] == Decimal("23.8000")


def test_standard_error_of_estimate_matches_exhibit_37():
    result = standard_error_of_estimate_from_mse("2.4")
    assert result["rounded_answer"] == Decimal("1.5492")


def test_prediction_standard_error_and_interval_match_npm_rdr_example():
    x_variation = sum_x_squared_deviations_from_sample_variance("4.285714", 8)
    sf = standard_error_of_forecast("1.8618987", 8, "5", "7.5", x_variation["final_answer"])
    interval = prediction_interval("10", "2.447", sf["final_answer"])
    assert sf["rounded_answer"] == Decimal("2.1499")
    assert interval["rounded_answer"]["lower_bound"] == Decimal("4.7391")
    assert interval["rounded_answer"]["upper_bound"] == Decimal("15.2609")


def test_prediction_standard_error_matches_rdr_equals_15_example():
    x_variation = sum_x_squared_deviations_from_sample_variance("4.285714", 8)
    sf = standard_error_of_forecast("1.8618987", 8, "15", "7.5", x_variation["final_answer"])
    assert sf["rounded_answer"] == Decimal("3.2249")


def test_linear_prediction_matches_amtex_example():
    result = predicted_value_simple_linear_regression("0.0095", "0.2354", "-0.01")
    assert result["rounded_answer"] == Decimal("0.0071")


def test_log_lin_level_forecast_matches_text_example():
    result = level_forecast_from_log_lin("-7", "2", "2.5")
    assert result["rounded_answer"] == Decimal("0.135335")


def test_mean_square_error_matches_roa_anova_example():
    result = mean_square_error("47.875", 6)
    assert result["rounded_answer"] == Decimal("11.9688")
