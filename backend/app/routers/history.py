from fastapi import APIRouter, HTTPException
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/history")
def history(limit: int = 50):
    with MortgageService() as s: return {"items": s.history(limit)}
@router.get("/history/{run_id}")
def history_run(run_id: int):
    with MortgageService() as s:
        item = s.history_run(run_id)
        if not item: raise HTTPException(404)
        return item
