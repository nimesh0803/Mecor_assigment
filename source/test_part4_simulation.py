import math
import pytest

try:
    # PYTHONPATH=source path-style imports
    from simulation import simulate, days_to_target
except ModuleNotFoundError:
    # package-style imports if you added source/__init__.py
    from source.simulation import simulate, days_to_target


def test_simulate_p1_includes_day0():
    # p=1.0 -> each referrer makes exactly 1 success per day until capacity (10 days).
    res = simulate(1.0, 12)
    # length = days+1; day0 baseline
    assert len(res) == 13
    assert res[0] == 0.0
    # Day i => 100 * min(i, 10)
    assert res[1] == 100.0
    assert res[5] == 500.0
    assert res[10] == 1000.0
    assert res[11] == 1000.0
    assert res[12] == 1000.0


def test_simulate_p0_all_zero():
    res = simulate(0.0, 5)
    assert res == [0.0] * 6


def test_days_to_target_basic():
    # p=1.0: Day 4 hits 400 >= 350
    assert days_to_target(1.0, 350) == 4
    # p=0.5: exp/day initially ~50; Day 3 -> ~150
    assert days_to_target(0.5, 150) == 3


def test_days_to_target_unachievable_and_edges():
    # Max possible = 100 * 10 = 1000
    assert days_to_target(0.7, 2000) is None
    # zero/negative targets return 0 days
    assert days_to_target(0.3, 0) == 0
    assert days_to_target(0.3, -5) == 0
    # p=0 and positive target -> impossible
    assert days_to_target(0.0, 1) is None


def test_monotone_non_decreasing():
    # sanity: cumulative is monotone
    res = simulate(0.37, 40)
    assert all(res[i] <= res[i + 1] + 1e-9 for i in range(len(res) - 1))
