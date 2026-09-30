from app.models import HomeRequest, PartyRequest, JewelryRequest, PlannerResult
from app.services.catalog import home_fallback, party_fallback, jewelry_fallback
from app.services.gemini_service import GeminiService

gemini=GeminiService()

def _normalize(planner, budget, fallback, ai):
    recs, allocation, total=fallback
    if ai and isinstance(ai,dict) and isinstance(ai.get("recommendations"),list):
        recs=ai["recommendations"][:10]
        allocation=ai.get("allocation") or allocation
        total=sum(float(x.get("subtotal", x.get("estimated_price",0))) for x in recs)
        summary=ai.get("summary", f"AI-generated {planner} plan.")
        used=True
    else:
        summary=f"A practical {planner} plan generated from the supplied budget and preferences."
        used=False
    total=min(total,budget)
    return PlannerResult(planner=planner,budget=budget,allocation={k:float(v) for k,v in allocation.items()},total_estimate=round(total,2),remaining=round(max(0,budget-total),2),summary=summary,recommendations=recs,ai_used=used)

def home(req:HomeRequest):
    return _normalize("home",req.budget,home_fallback(req),gemini.generate("home",req.model_dump()))

def party(req:PartyRequest):
    return _normalize("party",req.budget,party_fallback(req),gemini.generate("party",req.model_dump()))

def jewelry(req:JewelryRequest, image_bytes=None, mime_type=None):
    return _normalize("jewelry",req.budget,jewelry_fallback(req),gemini.generate("jewelry",req.model_dump(),image_bytes,mime_type))
