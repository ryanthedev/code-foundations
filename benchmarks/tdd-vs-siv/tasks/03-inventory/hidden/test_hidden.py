"""Hidden ground-truth suite for task 03 (Inventory discounts). Never shown.

  test_dw_*    — the new discount behavior the spec states
  test_offdw_* — existing behavior that must be PRESERVED + discount edges
                 the spec did not exemplify (regression surface)
"""
import pytest
from inventory import Inventory


# ---- DW-stated new behavior ------------------------------------------------

def test_dw_single_discounted_item():
    inv = Inventory()
    inv.add_item("a", 10, 2, discount=0.1)
    assert inv.total_value() == 18.0

def test_dw_sum_of_discounted_items():
    inv = Inventory()
    inv.add_item("a", 10, 2, discount=0.1)
    inv.add_item("b", 5, 4, discount=0)
    assert inv.total_value() == 38.0


# ---- Off-DW: preserved existing behavior + discount edges -------------------

def test_offdw_empty_inventory_is_zero():
    assert Inventory().total_value() == 0

def test_offdw_default_discount_is_zero():
    inv = Inventory()
    inv.add_item("a", 10, 3)          # no discount arg -> full price
    assert inv.total_value() == 30

def test_offdw_full_discount_contributes_zero():
    inv = Inventory()
    inv.add_item("a", 100, 5, discount=1.0)
    assert inv.total_value() == 0.0

def test_offdw_remove_item_still_works():
    inv = Inventory()
    inv.add_item("a", 10, 2)
    inv.add_item("b", 5, 1)
    inv.remove_item("a")
    assert inv.total_value() == 5

def test_offdw_remove_missing_item_raises():
    # existing behavior: del on a missing key raises KeyError
    with pytest.raises(KeyError):
        Inventory().remove_item("nope")
