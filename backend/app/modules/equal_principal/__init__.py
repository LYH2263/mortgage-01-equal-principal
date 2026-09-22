"""等额本金模块：每期本金固定为本金/期数，利息按当期期初余额乘月利率计，
月供 = 当期本金 + 当期利息，逐期递减；末期把剩余余额一次收干净。"""

METHOD = "equal_principal"


def schedule(principal: float, annual_rate: float, months: int) -> dict:
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    principal_each = P / n
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = bal if i == n else principal_each
        pay_i = principal_part + interest
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    return {
        "first_payment": rows[0]["payment"],
        "last_payment": rows[-1]["payment"],
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }
