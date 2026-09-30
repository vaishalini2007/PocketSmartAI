from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.models import RegisterRequest, LoginRequest, TokenResponse
from app.database import get_db
from app.auth import hash_password, verify_password, create_token, current_user

router=APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(data:RegisterRequest, request:Request):
    with get_db() as db:
        if db.execute("SELECT id FROM users WHERE email=?",(data.email.lower(),)).fetchone(): raise HTTPException(409,"Email already registered")
        cur=db.execute("INSERT INTO users(email,name,password_hash) VALUES(?,?,?)",(data.email.lower(),data.name.strip(),hash_password(data.password)))
        user_id=cur.lastrowid
    token=create_token(user_id); request.session["token"]=token
    return {"access_token":token,"token_type":"bearer"}

@router.post("/login", response_model=TokenResponse)
def login(data:LoginRequest, request:Request):
    with get_db() as db: row=db.execute("SELECT * FROM users WHERE email=?",(data.email.lower(),)).fetchone()
    if not row or not verify_password(data.password,row["password_hash"]): raise HTTPException(401,"Invalid email or password")
    token=create_token(row["id"]); request.session["token"]=token
    return {"access_token":token,"token_type":"bearer"}

@router.post("/logout")
def logout(request:Request):
    request.session.clear(); return {"message":"Logged out"}

@router.get("/session-info")
def session_info(user=__import__('fastapi').Depends(current_user)):
    return {"logged_in":True,"user":user}

@router.get("/session-data")
def session_data(user=__import__('fastapi').Depends(current_user)):
    return {"user":user,"message":"Session is active"}

@router.get("/token")
def token_alias(user=__import__('fastapi').Depends(current_user)):
    return {"access_token":create_token(user["id"]),"token_type":"bearer"}
