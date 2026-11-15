# tests/test_sheets.py
import pytest
from fastapi import HTTPException
import database
from app.api.endpoints.sheets import (
    create_custom_sheet,
    get_sheet_details,
    delete_custom_sheet_endpoint,
    list_sheets,
    CustomSheetCreateRequest
)

def test_custom_sheet_privacy_and_isolation():
    """
    Confirms strict multi-tenant isolation:
    User B cannot read or delete User A's custom curriculum sheet.
    """
    user_a, _ = database.register_user("alice@anvilbreaker.is-a.dev", "AlicePassword123", "alice")
    user_b, _ = database.register_user("bob@anvilbreaker.is-a.dev", "BobPassword123", "bob")

    # User A creates a custom roadmap
    req = CustomSheetCreateRequest(
        title="Alice Exclusive Sheet",
        description="Top secret algorithmic patterns",
        problems=[
            {"id": 9901, "title": "Hard DP on Trees", "difficulty": "H", "chapter_name": "Trees"},
            {"id": 9902, "title": "Advanced Monotonic Queue", "difficulty": "M", "chapter_name": "Queues"}
        ]
    )
    created = create_custom_sheet(payload=req, user_id=user_a["id"])
    slug = created["slug"]
    assert slug.startswith(f"user-{user_a['id']}-")

    # User A can read their own sheet
    sheet_data = get_sheet_details(slug=slug, user_id=user_a["id"])
    assert sheet_data["count"] == 2
    assert sheet_data["problems"][0]["title"] == "Hard DP on Trees"

    # User B attempts to read User A's sheet -> 404 Access Denied
    with pytest.raises(HTTPException) as exc_info:
        get_sheet_details(slug=slug, user_id=user_b["id"])
    assert exc_info.value.status_code == 404
    assert "access denied" in exc_info.value.detail.lower()

    # User B attempts to delete User A's sheet -> 404 Unauthorized
    with pytest.raises(HTTPException) as exc_del:
        delete_custom_sheet_endpoint(slug=slug, user_id=user_b["id"])
    assert exc_del.value.status_code == 404

def test_sheet_problem_counts_driven_from_loaded_data():
    """Verifies that system sheets compute problem counts directly from loaded collections."""
    sheets_info = list_sheets(user_id=1)
    sheets = sheets_info["sheets"]
    core = next(s for s in sheets if s["slug"] == "core-path")
    striver = next(s for s in sheets if s["slug"] == "striver-sde")
    neetcode = next(s for s in sheets if s["slug"] == "neetcode-150")
    blind = next(s for s in sheets if s["slug"] == "blind-75")

    assert core["problem_count"] > 0
    assert striver["problem_count"] == 95
    assert neetcode["problem_count"] >= 150
    assert blind["problem_count"] == 75
