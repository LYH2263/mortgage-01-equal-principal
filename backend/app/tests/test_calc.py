import pytest
from app.engines.amortization import (
    EQUAL_PAYMENT,
    EQUAL_PRINCIPAL,
    equal_payment_schedule,
    schedule,
)
from app.modules import equal_principal

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_default_method_is_equal_payment():
    assert schedule(1_000_000, 3.5, 360) == equal_payment_schedule(1_000_000, 3.5, 360)
    assert schedule(1_000_000, 3.5, 360, EQUAL_PAYMENT) == equal_payment_schedule(1_000_000, 3.5, 360)

def test_unknown_method_rejected():
    with pytest.raises(ValueError):
        schedule(100000, 3.5, 12, "weekly")

def test_equal_principal_first_and_last_payment():
    s = schedule(100000, 12, 10, EQUAL_PRINCIPAL)
    assert s["first_payment"] == 11000.0
    assert s["last_payment"] == 10100.0
    assert s["total_interest"] == 5500.0
    assert s["total_payment"] == 105500.0

def test_equal_principal_fixed_principal_and_decreasing_payment():
    s = schedule(1_000_000, 3.5, 360, EQUAL_PRINCIPAL)
    rows = s["rows"]
    assert len(rows) == 360
    # 每期本金固定为本金/期数（末期收干净除外）
    assert all(r["principal"] == rows[0]["principal"] for r in rows[:-1])
    # 相邻两期月供递减
    pays = [r["payment"] for r in rows]
    assert all(a > b for a, b in zip(pays, pays[1:]))
    # 末期余额收干净
    assert rows[-1]["balance"] == 0.0
    assert s["first_payment"] == rows[0]["payment"]
    assert s["last_payment"] == rows[-1]["payment"]
    assert s["total_payment"] == round(sum(r["payment"] for r in rows), 2)

def test_equal_principal_zero_rate():
    s = schedule(120000, 0, 12, EQUAL_PRINCIPAL)
    assert s["total_interest"] == 0.0
    assert s["first_payment"] == s["last_payment"] == 10000.0

def test_equal_principal_bad_months():
    with pytest.raises(ValueError):
        schedule(100, 3, 0, EQUAL_PRINCIPAL)

def test_module_matches_engine_path():
    assert equal_principal.schedule(800000, 4.2, 240) == schedule(800000, 4.2, 240, EQUAL_PRINCIPAL)
    assert equal_principal.METHOD == EQUAL_PRINCIPAL
