# app/core/dependencies.py
from typing import Optional
from fastapi import Header, HTTPException
import database

def get_authenticated_user_id(authorization: Optional[str] = Header(None)) -> int:
    """
    Enforces authentication for mutating routes.
    Requires Authorization: Bearer <session_token>.
    Rejects any unauthenticated or header-impersonated requests.
    """
    if not authorization or not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Authentication required. Please sign in to access your private vault."
        )
    
    token = authorization.split(" ", 1)[1].strip()
    user = database.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired session. Please sign in again."
        )
    
    return user["id"]

def get_optional_user_id(authorization: Optional[str] = Header(None)) -> int:
    """
    Resolves authenticated user if Bearer token is provided.
    Falls back to local development user (id 1) for read-only queries.
    Never creates arbitrary users from untrusted headers.
    """
    if authorization and isinstance(authorization, str) and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        user = database.get_user_by_token(token)
        if user:
            return user["id"]
    
    # Safe standalone fallback to default local user (ID 1)
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = 'local_user'")
    row = c.fetchone()
    conn.close()
    if row:
        return row["id"]
    return 1
