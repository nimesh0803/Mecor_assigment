# Part 3 tests: unique reach expansion + flow centrality (forest, read-only)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
try:
    # If you run with:  set PYTHONPATH=source  (Windows) / export PYTHONPATH=source (Unix)
    from referral_network import ReferralNetwork
except ModuleNotFoundError:
    # If you added source/__init__.py and use package imports
    from source.referral_network import ReferralNetwork


def build_sample_forest():
    """
    Valid forest (unique parent per node):
        A -> B, C
        B -> D
        C -> E
        F -> G, H
    """
    g = ReferralNetwork()
    g.add_referral("A", "B")
    g.add_referral("A", "C")
    g.add_referral("B", "D")
    g.add_referral("C", "E")
    g.add_referral("F", "G")
    g.add_referral("F", "H")
    return g


def test_unique_reach_expansion_basic():
    g = build_sample_forest()
    picks = g.unique_reach_expansion(2)
    # A covers {B,C,D,E} = 4; next best F covers {G,H} = 2
    assert picks[0] == ("A", 4)
    assert picks[1] == ("F", 2)


def build_broker_forest():
    """
    Valid broker-like shape without violating Part 1:
        A -> B -> C -> F
                  └-> G
        A -> E
    """
    g = ReferralNetwork()
    g.add_referral("A", "B")
    g.add_referral("B", "C")
    g.add_referral("C", "F")
    g.add_referral("C", "G")
    g.add_referral("A", "E")
    return g


def test_flow_centrality_ranking():
    g = build_broker_forest()
    ranks = g.flow_centrality()
    # By formula: score(v) = ancestors(v) * descendants(v)
    # C: anc=2 (A,B), desc=2 (F,G) => 4
    # B: anc=1 (A),   desc=3 (C,F,G) => 3
    assert ranks[0] == ("C", 4)
    assert ("B", 3) in ranks
    # Check read-only behavior: counts unchanged after call
    # (indirect check: parent/children remain consistent)
    assert g.parent_of("B") == "A"
    assert set(g.get_direct_referrals("C")) == {"F", "G"}
