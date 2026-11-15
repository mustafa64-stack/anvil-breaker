# app/api/endpoints/auth.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
import database
from app.core.dependencies import get_authenticated_user_id

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ConnectRequest(BaseModel):
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    preferred_browser: Optional[str] = None

@router.post("/register")
def register_endpoint(payload: RegisterRequest):
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email address is required")
    if not payload.password or len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    user, err = database.register_user(email, payload.password, payload.username)
    if err:
        raise HTTPException(status_code=400, detail=err)
    
    token = user.pop("session_token", "")
    user.pop("password_hash", None)
    return {
        "status": "ok",
        "user": user,
        "token": token
    }

@router.post("/login")
def login_endpoint(payload: LoginRequest):
    identifier = payload.email.strip()
    if not identifier or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user, err = database.authenticate_user(identifier, payload.password)
    if err:
        raise HTTPException(status_code=401, detail=err)
    
    token = user.pop("session_token", "")
    user.pop("password_hash", None)
    return {
        "status": "ok",
        "user": user,
        "token": token
    }

@router.get("/me")
def get_current_user_profile(user_id: int = Depends(get_authenticated_user_id)):
    user = database.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User vault not found")
    user.pop("password_hash", None)
    user.pop("session_token", None)
    return {"status": "ok", "user": user}

@router.post("/connect")
def connect_accounts_endpoint(
    payload: ConnectRequest, 
    user_id: int = Depends(get_authenticated_user_id)
):
    user = database.update_user_connections(
        user_id=user_id,
        github_username=payload.github_username,
        leetcode_username=payload.leetcode_username,
        preferred_browser=payload.preferred_browser
    )
    user.pop("password_hash", None)
    user.pop("session_token", None)
    return {"status": "ok", "user": user}

@router.post("/logout")
def logout_endpoint(user_id: int = Depends(get_authenticated_user_id)):
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET session_token = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Signed out successfully"}
