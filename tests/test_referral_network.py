# tests/test_referral_network.py
import sys
import os
import pytest
from source.referral_network import ReferralNetwork
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_direct_referrals_basic():
    g = ReferralNetwork()
    g.add_referral("A", "B")
    g.add_referral("A", "C")
    assert g.get_direct_referrals("A") == ["B", "C"]
    assert g.get_direct_referrals("B") == []

def test_no_self_referral():
    g = ReferralNetwork()
    g.add_user("X")
    with pytest.raises(ValueError, match="no self-referrals"):
        g.add_referral("X", "X")

def test_unique_referrer_enforced():
    g = ReferralNetwork()
    g.add_referral("A", "B")
    # duplicate (same edge) is idempotent
    assert g.add_referral("A", "B") is False
    # different referrer -> should fail
    with pytest.raises(ValueError, match="unique referrer"):
        g.add_referral("C", "B")

def test_cycle_prevention():
    g = ReferralNetwork()
    g.add_referral("A", "B")
    g.add_referral("B", "C")
    with pytest.raises(ValueError, match="cycle"):
        g.add_referral("C", "A")  # would create A<-C path

def test_implicit_user_creation_and_parent_lookup():
    g = ReferralNetwork()
    g.add_referral("R1", "X")
    assert g.users() == ["R1", "X"]
    assert g.parent_of("X") == "R1"
    assert g.parent_of("R1") is None
