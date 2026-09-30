from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.auth import current_user
from app.models import HomeRequest, PartyRequest, JewelryRequest
from app.services.recommendation_service import home, party, jewelry
from app.services.history import save_history

router=APIRouter()

@router.post("/generate-home")
def generate_home(data:HomeRequest,user=Depends(current_user)):
    result=home(data); save_history(user["id"],"home",data.model_dump(),result); return result

@router.post("/generate-party")
def generate_party(data:PartyRequest,user=Depends(current_user)):
    result=party(data); save_history(user["id"],"party",data.model_dump(),result); return result

@router.post("/generate-jewelry")
async def generate_jewelry(budget:float=Form(...),occasion:str=Form(...),style:str=Form("Elegant"),metal:str=Form("Any"),notes:str=Form(""),image:UploadFile|None=File(None),user=Depends(current_user)):
    data=JewelryRequest(budget=budget,occasion=occasion,style=style,metal=metal,notes=notes)
    image_bytes=await image.read() if image else None
    result=jewelry(data,image_bytes,image.content_type if image else None); save_history(user["id"],"jewelry",data.model_dump(),result); return result

@router.get("/recommendations-details")
def recommendation_details(user=Depends(current_user)):
    return {"message":"Use the planner endpoints to generate recommendations.","supported_planners":["home","party","jewelry"]}
