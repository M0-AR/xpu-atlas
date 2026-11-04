import math

from xpu_atlas.analyze import cagr, exponential_fit, max_drawdown, pearson, rankdata, spearman


def test_cagr_basic_growth_and_decline():
    assert abs(cagr(100.0, 200.0, 1.0) - 1.0) < 1e-12
    assert abs(cagr(100.0, 50.0, 2.0) - (math.sqrt(0.5) - 1.0)) < 1e-12
    assert math.isnan(cagr(0.0, 1.0, 1.0))


def test_max_drawdown():
    assert abs(max_drawdown([100, 50, 75]) - (-0.5)) < 1e-12
    assert max_drawdown([100, 120, 150]) == 0.0


def test_correlations():
    assert abs(pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-12
    assert abs(pearson([1, 2, 3], [6, 4, 2]) + 1.0) < 1e-12
    assert abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-12


def test_rankdata_handles_ties():
    assert rankdata([10, 20, 20, 30]) == [1.0, 2.5, 2.5, 4.0]


def test_exponential_fit_exact_doubling():
    counts = {str(2000 + i): 2**i for i in range(8)}
    fit = exponential_fit(counts)
    assert abs(fit["doubling_years"] - 1.0) < 1e-9
    assert abs(fit["r_squared"] - 1.0) < 1e-9
    assert fit["fit_quality"] == "good"
