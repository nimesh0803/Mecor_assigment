"""
Part 4 — Network Growth Simulation (READ THIS):
- Deterministic expected-value model (no Monte Carlo).
- Start with N0=100 active referrers; each has lifetime capacity C=10.
- On each day, each active referrer can produce at most one successful referral with prob p.
- A referrer becomes inactive once they accumulate C successes (absorbing cap).
- New referrals DO NOT become referrers (per spec; only initial referrers are active).
- simulate(p, days) returns a list "cum[i]" = expected total referrals by end of day i, i=0..days.
- days_to_target(p, target_total) returns the minimum day d with cum[d] >= target_total, or None if target_total > N0*C.

Complexity:
- simulate:  O(days * C) via DP on a single-referrer success distribution, then scale by N0.
- days_to_target: O(d * C), where d is the returned day (early-exit). Both C and N0 are constants (10, 100).
"""

from typing import List, Optional

DEFAULT_INITIAL = 100
DEFAULT_CAPACITY = 10


def _next_dist(dist: List[float], p: float, cap: int) -> List[float]:
    """
    DP transition for a single referrer:
    dist[k] = Prob(have exactly k successes so far), for k in [0..cap], with cap absorbing.
    One day passes: from k<cap -> k (fail) with (1-p), -> k+1 (success) with p; k==cap stays.
    """
    nxt = [0.0] * (cap + 1)
    # stay at 0 on failure
    nxt[0] = dist[0] * (1.0 - p)
    # 1..cap-1 transitions
    for k in range(1, cap):
        nxt[k] = dist[k] * (1.0 - p) + dist[k - 1] * p
    # absorbing cap: either was already cap or got a success from cap-1
    nxt[cap] = dist[cap] + dist[cap - 1] * p
    return nxt


def simulate(
    p: float,
    days: int,
    initial_referrers: int = DEFAULT_INITIAL,
    capacity: int = DEFAULT_CAPACITY,
) -> List[float]:
    """
    [Part 4] Return cumulative expected referrals per day.
    - Length = days + 1. cum[0] = 0 (end of day 0 / before any activity).
    - For i>=1: cum[i] = initial_referrers * E[min(Binomial(i, p), capacity)].
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0,1]")
    if days < 0 or initial_referrers < 0 or capacity < 0:
        raise ValueError("days, initial_referrers, capacity must be >= 0")

    # distribution for a single referrer over successes 0..capacity
    dist = [0.0] * (capacity + 1)
    dist[0] = 1.0

    out = [0.0] * (days + 1)  # cum[0] = 0
    if days == 0:
        return out

    for d in range(1, days + 1):
        dist = _next_dist(dist, p, capacity)
        # expected successes for ONE referrer at end of day d:
        exp_one = sum(k * prob for k, prob in enumerate(dist))
        out[d] = initial_referrers * exp_one
    return out


def days_to_target(
    p: float,
    target_total: int,
    initial_referrers: int = DEFAULT_INITIAL,
    capacity: int = DEFAULT_CAPACITY,
) -> Optional[int]:
    """
    [Part 4] Minimum days d s.t. simulate(p, d)[d] >= target_total.
    - Returns 0 if target_total <= 0.
    - Returns None if target_total > initial_referrers * capacity (unachievable).
    - Otherwise iterates day-by-day with early exit.
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0,1]")
    if target_total <= 0:
        return 0
    max_total = initial_referrers * capacity
    if target_total > max_total:
        return None
    if p == 0.0:
        return None  # can't make progress toward a positive target

    # iterate DP until we cross target
    dist = [0.0] * (capacity + 1)
    dist[0] = 1.0
    day = 0
    cum = 0.0
    while cum < target_total:
        day += 1
        dist = _next_dist(dist, p, capacity)
        exp_one = sum(k * prob for k, prob in enumerate(dist))
        cum = initial_referrers * exp_one
        # loop will end once cum >= target_total
    return day
