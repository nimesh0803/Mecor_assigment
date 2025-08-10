import math
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from source.bonus_opt import min_bonus_for_target

# Helpers: monotone adoption functions
def linear_prob(divisor):
    return lambda b: min(1.0, max(0.0, b / divisor))

def logistic_prob(scale=200.0, cap=0.95):
    # smooth, monotone, saturates below 1
    import math
    return lambda b: cap * (1 - math.exp(-b / scale))


def test_linear_days_leq_cap_exact_hits():
    # days=10: cap not exceeded; E = 100 * 10 * p when p<=1 (cap equals days)
    # Target 500 -> need p=0.5 -> with p=b/1000 => b=500
    b = min_bonus_for_target(days=10, target_hires=500, adoption_prob=linear_prob(1000))
    assert b == 500

    # Full capacity 1000 needs p=1.0 -> b=1000 (since p=min(1, b/1000))
    b = min_bonus_for_target(days=10, target_hires=1000, adoption_prob=linear_prob(1000))
    assert b == 1000


def test_rounds_up_to_next_10():
    # days=2: E = 100 * 2 * p = 200p
    # target 101 -> need p >= 0.505
    # with p=b/200 => b >= 101 -> must round UP to $110
    b = min_bonus_for_target(days=2, target_hires=101, adoption_prob=linear_prob(200))
    assert b == 110


def test_unachievable_due_to_hard_limit():
    # Max by day 3 is 100 * 3 = 300 no matter what bonus is
    b = min_bonus_for_target(days=3, target_hires=400, adoption_prob=linear_prob(1))
    assert b is None


def test_unachievable_due_to_prob_ceiling():
    # adoption prob saturates at 0.95, days=10 -> E <= 100 * 10 * 0.95 = 950
    b = min_bonus_for_target(days=10, target_hires=960, adoption_prob=logistic_prob(scale=200, cap=0.95))
    assert b is None


def test_zero_target_returns_zero_bonus():
    b = min_bonus_for_target(days=7, target_hires=0, adoption_prob=linear_prob(1000))
    assert b == 0
