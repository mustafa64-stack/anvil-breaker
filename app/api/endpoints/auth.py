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

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str

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
    if err == "USER_EXISTS":
        raise HTTPException(status_code=400, detail="USER_EXISTS: An account with this email already exists. Switched to Sign In.")
    elif err:
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
    if err == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND: No account found with this email. Would you like to create one?")
    elif err == "INCORRECT_PASSWORD":
        raise HTTPException(status_code=401, detail="INCORRECT_PASSWORD: Incorrect password. Click 'Forgot password?' below to reset it.")
    elif err:
        raise HTTPException(status_code=401, detail=err)
    
    token = user.pop("session_token", "")
    user.pop("password_hash", None)
    return {
        "status": "ok",
        "user": user,
        "token": token
    }

@router.post("/forgot-password")
def forgot_password_endpoint(payload: ForgotPasswordRequest):
    clean_email = payload.email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=400, detail="Valid email address is required")
    
    res, err = database.request_password_reset(clean_email)
    if err:
        raise HTTPException(status_code=404, detail=err)
    
    return {
        "status": "ok",
        "message": f"Verification code generated for {clean_email}. Valid for 20 minutes.",
        "reset_code": res["reset_code"],
        "email": res["email"]
    }

@router.post("/reset-password")
def reset_password_endpoint(payload: ResetPasswordRequest):
    clean_email = payload.email.strip().lower()
    if not clean_email or not payload.reset_code:
        raise HTTPException(status_code=400, detail="Email and 6-digit reset code are required")
    if not payload.new_password or len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    user, err = database.reset_password(clean_email, payload.reset_code, payload.new_password)
    if err:
        raise HTTPException(status_code=400, detail=err)
    
    token = user.pop("session_token", "")
    user.pop("password_hash", None)
    return {
        "status": "ok",
        "message": "Password reset successfully! Vault unlocked.",
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

