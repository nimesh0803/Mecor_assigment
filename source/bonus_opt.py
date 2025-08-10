"""
Part 5 — Referral Bonus Optimization (READ-ONLY; uses Part 4 simulate)

Spec:
- Bonus paid in $10 increments. adoption_prob(bonus) -> p in [0,1], monotone non-decreasing.
- Find the MINIMUM bonus (rounded UP to nearest $10) so expected hires by end of `days`
  meet/exceed `target_hires`. Return None if unachievable.
- Fixed N0=100 initial referrers and capacity C=10. (Part 4 model)
Time:
- Each simulate call is O(days * C). We do O(log B) simulate calls via exponential+binary search.
"""

from typing import Callable, Optional
from simulation import simulate, DEFAULT_INITIAL, DEFAULT_CAPACITY  # N0=100, C=10

def min_bonus_for_target(
    days: int,
    target_hires: int,
    adoption_prob: Callable[[int], float],
    eps: float = 1e-3,
    bonus_step: int = 10,
) -> Optional[int]:
    if days < 0 or target_hires < 0 or bonus_step <= 0:
        raise ValueError("days, target_hires >= 0 and bonus_step > 0 required")

    # Upper bound check (p<=1): max expected by day d is N0 * min(d, C)
    max_possible = DEFAULT_INITIAL * min(days, DEFAULT_CAPACITY)
    if target_hires == 0:
        return 0
    if target_hires > max_possible:
        return None

    def expected_at_bonus(bonus: int) -> float:
        p = float(adoption_prob(bonus))
        if p < 0.0: p = 0.0
        if p > 1.0: p = 1.0
        return simulate(p, days)[days]  # cumulative expected hires at end of `days`

    # If zero bonus already hits target, done.
    if expected_at_bonus(0) + eps >= target_hires:
        return 0

    # Exponential search to bracket the solution on multiples of bonus_step
    lo_units = 0
    hi_units = 1
    hi_val = expected_at_bonus(hi_units * bonus_step)
    it = 0
    # Stop if adoption_prob saturates (p≈1) yet still below target -> impossible
    while hi_val + eps < target_hires and it < 60:
        hi_units *= 2
        hi_val = expected_at_bonus(hi_units * bonus_step)
        it += 1
        # Early impossible check if p≈1 and still not enough (covers monotone "black box")
        p_hi = float(adoption_prob(hi_units * bonus_step))
        if p_hi >= 1.0 - eps and hi_val + eps < target_hires:
            return None
    if hi_val + eps < target_hires:
        return None  # failed to bracket within sane range

    # Binary search on units (each unit = $bonus_step)
    lo, hi = lo_units, hi_units
    while lo < hi:
        mid = (lo + hi) // 2
        mval = expected_at_bonus(mid * bonus_step)
        if mval + eps >= target_hires:
            hi = mid
        else:
            lo = mid + 1
    return lo * bonus_step
