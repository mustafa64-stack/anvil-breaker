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

def test_case_insensitive_authentication():
    """Confirms user can register with mixed case and log in with lowercase or mixed case."""
    email = "CaseTestUser@AnvilBreaker.is-a.dev"
    password = "SafePassword123"
    reg_user, err = database.register_user(email, password, "CaseUser")
    assert err is None or err == "USER_EXISTS"

    # Login with lowercase email
    auth_user, err = database.authenticate_user(email.lower(), password)
    assert err is None
    assert auth_user["email"] == email.lower()

    # Login with uppercase email
    auth_user2, err = database.authenticate_user(email.upper(), password)
    assert err is None

def test_forgot_and_reset_password_workflow():
    """Confirms request_password_reset generates valid code and reset_password updates password."""
    email = "reset_user_test@anvilbreaker.is-a.dev"
    old_pass = "OldPassword123"
    new_pass = "NewSuperPassword456"
    reg_user, _ = database.register_user(email, old_pass, "resetuser")

    res, err = database.request_password_reset(email)
    assert err is None
    code = res["reset_code"]
    assert len(code) == 6

    # Wrong code should fail
    _, err_wrong = database.reset_password(email, "000000", new_pass)
    assert err_wrong is not None

    # Correct code succeeds
    updated, err_ok = database.reset_password(email, code, new_pass)
    assert err_ok is None

    # Old password fails
    _, err_old = database.authenticate_user(email, old_pass)
    assert err_old == "INCORRECT_PASSWORD"

    # New password succeeds
    login_user, err_new = database.authenticate_user(email, new_pass)
    assert err_new is None
    assert login_user["email"] == email

