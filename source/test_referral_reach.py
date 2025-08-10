import pytest
try:
    # if you run with PYTHONPATH=source
    from referral_network import ReferralNetwork
except ModuleNotFoundError:
    # if you made source a package (source/__init__.py)
    from source.referral_network import ReferralNetwork

def build_sample():
    g = ReferralNetwork()
    # A tree
    g.add_referral("A", "B")
    g.add_referral("A", "C")
    g.add_referral("B", "D")
    g.add_referral("C", "E")
    # A second tree
    g.add_referral("F", "G")
    g.add_referral("F", "H")
    return g

def test_reach_counts():
    g = build_sample()
    assert g.reach_count("A") == 4    # B,C,D,E
    assert g.reach_count("B") == 1    # D
    assert g.reach_count("C") == 1    # E
    assert g.reach_count("D") == 0
    assert g.reach_count("Z") == 0    # unknown

def test_top_k():
    g = build_sample()
    top3 = g.top_k_referrers_by_reach(3)
    assert top3 == [("A", 4), ("F", 2), ("B", 1)]  # tie B/C broken by id
    assert g.top_k_referrers_by_reach(0) == []
    # k > number of users -> returns all
    all_ranked = g.top_k_referrers_by_reach(100)
    assert all_ranked[0] == ("A", 4)
    assert ("D", 0) in all_ranked and ("H", 0) in all_ranked
