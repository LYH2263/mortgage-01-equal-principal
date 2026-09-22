from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.mortgage_service import MortgageService
router = APIRouter()
class SettingsUpdate(BaseModel):
    method: Literal["equal_payment", "equal_principal"] | None = None
@router.get("/settings")
def settings():
    with MortgageService() as s: return s.settings()
@router.put("/settings")
def put_settings(body: SettingsUpdate):
    with MortgageService() as s: return s.update_settings(body.model_dump(exclude_none=True))
