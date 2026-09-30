from fastapi import APIRouter, Depends
from app.auth import current_user
from app.services.history import get_history
router=APIRouter()
@router.get("/history")
def history(user=Depends(current_user)): return get_history(user["id"])
