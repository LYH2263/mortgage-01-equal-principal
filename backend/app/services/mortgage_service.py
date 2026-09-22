import json
from app.db import connect
from app.engines import amortization
from app.repositories import loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def update_settings(self, changes):
        for k, v in changes.items(): settings.set_value(self._c, k, v)
        return self.settings()
    def history(self, limit=50): return [self._decorate(r) for r in runs.list_recent(self._c, limit)]
    def history_run(self, run_id):
        row = runs.get(self._c, run_id)
        return self._decorate(row) if row else None
    def _decorate(self, row):
        item = dict(row)
        try: payload = json.loads(item.get("input_json") or "{}")
        except json.JSONDecodeError: payload = {}
        try: result = json.loads(item.get("result_json") or "{}")
        except json.JSONDecodeError: result = {}
        # 老记录未写 method 时按等额本息对待；展示数以写入时为准，不随系统默认变化
        item["method"] = result.get("method") or payload.get("method") or "equal_payment"
        item["total_interest"] = result.get("total_interest")
        item["input"] = payload
        item["result"] = result
        return item
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, method="equal_payment"):
        full = amortization.schedule(principal, annual_rate, months, method)
        out = {"method": method}
        for k in ("monthly_payment", "first_payment", "last_payment", "total_interest", "total_payment"):
            if k in full: out[k] = full[k]
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule",
                {"principal": principal, "annual_rate": annual_rate, "months": months, "method": method}, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
