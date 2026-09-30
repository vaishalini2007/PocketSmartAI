from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers import auth, planners, history

BASE=Path(__file__).resolve().parent
settings=get_settings()
app=FastAPI(title=settings.app_name, version="1.0.0", description="GenAI budget and recommendation assistant")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, max_age=43200, same_site="lax", https_only=False)
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates=Jinja2Templates(directory=str(BASE/"templates"))
app.mount("/static", StaticFiles(directory=str(BASE/"static")), name="static")
app.include_router(auth.router, prefix="/api")
app.include_router(planners.router, prefix="/api")
app.include_router(history.router, prefix="/api")

@app.on_event("startup")
def startup(): init_db()

@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name}

@app.get("/",response_class=HTMLResponse)
def index(request:Request): return templates.TemplateResponse("index.html",{"request":request})
@app.get("/login",response_class=HTMLResponse)
def login_page(request:Request): return templates.TemplateResponse("login.html",{"request":request})
@app.get("/register",response_class=HTMLResponse)
def register_page(request:Request): return templates.TemplateResponse("register.html",{"request":request})
@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request): return templates.TemplateResponse("dashboard.html",{"request":request})
@app.get("/planner/{planner}",response_class=HTMLResponse)
def planner_page(request:Request,planner:str):
    if planner not in {"home","party","jewelry"}: return RedirectResponse("/")
    return templates.TemplateResponse(f"{planner}.html",{"request":request,"planner":planner})
@app.get("/history",response_class=HTMLResponse)
def history_page(request:Request): return templates.TemplateResponse("history.html",{"request":request})

if __name__ == "__main__":
    import uvicorn; uvicorn.run("app.main:app",host="127.0.0.1",port=8000,reload=True)
