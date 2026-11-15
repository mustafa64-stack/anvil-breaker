# tests/test_export.py
import json
import pytest
import database
from app.api.endpoints.progress import export_backup, update_status, StatusUpdateRequest

def test_export_backup_scrubs_sensitive_credentials():
    """
    Phase 1 Security Requirement:
    /api/export must strictly strip password_hash and session_token from the user object,
    and include the user's username in the Content-Disposition filename header.
    """
    user, _ = database.register_user("vaultuser@anvilbreaker.is-a.dev", "SecurePass987!", "vaultuser")
    user_id = user["id"]

    # Record a solve
    req = StatusUpdateRequest(problem_id=1, status="clean", time_spent=300, sm2_quality=5)
    update_status(payload=req, user_id=user_id)

    # Call export endpoint
    response = export_backup(user_id=user_id)
    assert response.status_code == 200

    # Verify download header
    disposition = response.headers.get("Content-Disposition", "")
    assert "dsa_backup_vaultuser_" in disposition
    assert ".json" in disposition

    # Parse exported payload
    payload = json.loads(response.body.decode("utf-8"))
    exported_user = payload["user"]

    # Strictly check that credentials are not leaked
    assert "password_hash" not in exported_user
    assert "session_token" not in exported_user
    assert exported_user["username"] == "vaultuser"
    assert exported_user["email"] == "vaultuser@anvilbreaker.is-a.dev"

    # Check progress data is present
    assert len(payload["progress"]) >= 1
    assert payload["progress"][0]["problem_id"] == 1
