from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(hours=12)}
    return jwt.encode(payload, get_settings().secret_key, algorithm="HS256")

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        return int(payload["sub"])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

def current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    token = request.session.get("token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user_id = decode_token(token)
    with get_db() as db:
        row = db.execute("SELECT id, email, name FROM users WHERE id=?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return dict(row)
