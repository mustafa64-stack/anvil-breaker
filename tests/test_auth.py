# tests/test_auth.py
import pytest
from fastapi import HTTPException
import database
from app.core.dependencies import get_authenticated_user_id, get_optional_user_id
from app.api.endpoints.auth import register_endpoint, login_endpoint, RegisterRequest, LoginRequest

def test_rejected_header_impersonation_without_token():
    """Mutating routes must reject requests with no Authorization header."""
    with pytest.raises(HTTPException) as exc_info:
        get_authenticated_user_id(authorization=None)
    assert exc_info.value.status_code == 401
    assert "Authentication required" in exc_info.value.detail

def test_rejected_header_impersonation_with_invalid_token():
    """Mutating routes must reject spoofed or forged Bearer tokens."""
    with pytest.raises(HTTPException) as exc_info:
        get_authenticated_user_id(authorization="Bearer spoofed_token_xyz_12345")
    assert exc_info.value.status_code == 401
    assert "Invalid or expired session" in exc_info.value.detail

def test_authenticated_user_resolution_with_valid_bearer_token():
    """Valid Bearer tokens securely resolve to the authenticated user ID."""
    user, err = database.register_user("testuser@anvilbreaker.is-a.dev", "SecretPassword123", "testuser")
    assert err is None
    token = user["session_token"]
    assert token is not None

    resolved_id = get_authenticated_user_id(authorization=f"Bearer {token}")
    assert resolved_id == user["id"]

def test_optional_user_id_does_not_create_users_from_untrusted_input():
    """Optional user resolver must fall back safely and never create users."""
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM users")
    count_before = c.fetchone()["count"]
    conn.close()

    uid = get_optional_user_id(authorization=None)
    assert isinstance(uid, int)

    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM users")
    count_after = c.fetchone()["count"]
    conn.close()

    assert count_after == count_before
