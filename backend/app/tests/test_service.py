import os
import tempfile

# 必须在导入任何 app 模块前指向独立数据目录，避免污染开发库
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="mortgage-test-")

import pytest
from pydantic import ValidationError

from app import seed
from app.db import connect
from app.schemas.schedule import ScheduleRequest
from app.services.mortgage_service import MortgageService


@pytest.fixture()
def svc():
    seed.init_db()
    conn = connect()
    conn.execute("DELETE FROM calc_runs")
    conn.commit()
    conn.close()
    s = MortgageService()
    yield s
    s.close()


def _run_count():
    conn = connect()
    n = conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    conn.close()
    return n


def test_default_method_keeps_equal_payment_numbers(svc):
    out = svc.schedule(1_000_000, 3.5, 360, None, False)
    assert out["method"] == "equal_payment"
    assert out["monthly_payment"] == 4490.45
    assert out["run_id"] is None


def test_equal_principal_response_fields(svc):
    out = svc.schedule(1_000_000, 3.5, 360, None, False, 12, "equal_principal")
    assert out["method"] == "equal_principal"
    assert "monthly_payment" not in out
    assert out["first_payment"] > out["last_payment"]
    assert out["total_interest"] > 0
    assert out["total_payment"] == round(1_000_000 + out["total_interest"], 2)
    pays = [r["payment"] for r in out["preview"]]
    assert all(a > b for a, b in zip(pays, pays[1:]))


def test_persist_false_writes_nothing(svc):
    before = _run_count()
    out = svc.schedule(800000, 4.2, 240, None, False, 12, "equal_principal")
    assert out["run_id"] is None
    assert _run_count() == before


def test_persist_true_pins_method_and_details(svc):
    out = svc.schedule(800000, 4.2, 240, None, True, 6, "equal_principal")
    assert out["run_id"] is not None
    row = svc.history_run(out["run_id"])
    assert row["method"] == "equal_principal"
    assert row["total_interest"] == out["total_interest"]
    assert row["input"]["method"] == "equal_principal"
    assert row["result"]["first_payment"] == out["first_payment"]
    assert row["result"]["preview"] == out["preview"]


def test_history_run_survives_default_method_change(svc):
    out = svc.schedule(800000, 4.2, 240, None, True, 6, "equal_principal")
    rid = out["run_id"]
    # 系统默认方式改回等额本息后，历史记录展示数不得跟着变
    svc.update_settings({"method": "equal_payment"})
    assert svc.settings()["method"] == "equal_payment"
    row = svc.history_run(rid)
    assert row["method"] == "equal_principal"
    assert row["total_interest"] == out["total_interest"]
    assert row["result"]["last_payment"] == out["last_payment"]


def test_history_run_missing_returns_none(svc):
    assert svc.history_run(999999) is None


def test_invalid_method_rejected_without_write(svc):
    before = _run_count()
    with pytest.raises(ValueError):
        svc.schedule(800000, 4.2, 240, None, True, 12, "weekly")
    assert _run_count() == before


def test_request_validation_boundaries():
    with pytest.raises(ValidationError):
        ScheduleRequest(principal=0, annual_rate=3.5, months=360)
    with pytest.raises(ValidationError):
        ScheduleRequest(principal=100, annual_rate=-0.1, months=360)
    with pytest.raises(ValidationError):
        ScheduleRequest(principal=100, annual_rate=3.5, months=0)
    with pytest.raises(ValidationError):
        ScheduleRequest(principal=100, annual_rate=3.5, months=601)
    with pytest.raises(ValidationError):
        ScheduleRequest(principal=100, annual_rate=3.5, months=12, method="weekly")
    ok = ScheduleRequest(principal=100, annual_rate=3.5, months=12)
    assert ok.method == "equal_payment"
