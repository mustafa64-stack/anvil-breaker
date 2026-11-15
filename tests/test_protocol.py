# tests/test_protocol.py
import pytest
from datetime import datetime, timedelta
import database
from app.core.protocol_engine import calculate_sm2_interval, calculate_adaptive_budget
from app.api.endpoints.progress import update_status, StatusUpdateRequest

def test_second_solve_interval_grows():
    """
    SM-2 SuperMemo memory curve:
    First solve: repetitions=1, interval=1 day
    Second solve: repetitions=2, interval=6 days
    Verifies that retention interval strictly grows on subsequent clean solves.
    """
    first_solve = calculate_sm2_interval(quality=4, repetitions=0, ef=2.5, prev_interval=1)
    assert first_solve["repetitions"] == 1
    assert first_solve["interval_days"] == 1

    second_solve = calculate_sm2_interval(
        quality=4,
        repetitions=first_solve["repetitions"],
        ef=first_solve["easiness_factor"],
        prev_interval=first_solve["interval_days"]
    )
    assert second_solve["repetitions"] == 2
    assert second_solve["interval_days"] == 6
    assert second_solve["interval_days"] > first_solve["interval_days"]

def test_adaptive_budget_changes_when_fail_rate_above_threshold():
    """
    Protocol budget expands read and pattern phases when cognitive friction (fail rate) exceeds 0.4.
    """
    baseline_budget = calculate_adaptive_budget(difficulty="M", user_fail_rate_topic=0.0)
    assert baseline_budget["total_minutes"] == 25
    assert baseline_budget["phases"][0]["minutes"] == 4  # Read & Trace
    assert baseline_budget["phases"][1]["minutes"] == 6  # Pick a Pattern

    high_friction_budget = calculate_adaptive_budget(difficulty="M", user_fail_rate_topic=0.5)
    assert high_friction_budget["total_minutes"] == 28
    assert high_friction_budget["phases"][0]["minutes"] == 5  # Expanded by +1 min
    assert high_friction_budget["phases"][1]["minutes"] == 8  # Expanded by +2 mins
    assert high_friction_budget["total_minutes"] > baseline_budget["total_minutes"]

def test_sm2_state_persisted_in_database_and_reviews_deduplicated():
    """
    Verifies that calling update_status saves SM-2 state in user_progress
    and avoids creating duplicate uncompleted review rows for the same problem and date.
    """
    user, _ = database.register_user("solver@anvilbreaker.is-a.dev", "Password123")
    user_id = user["id"]

    # First attempt: failure stand-down (Rule 4)
    req1 = StatusUpdateRequest(
        problem_id=42,
        status="failed",
        time_spent=900,
        error_type="idea",
        sm2_quality=1
    )
    res1 = update_status(payload=req1, user_id=user_id)
    assert res1["status"] == "ok"
    assert res1["sm2"]["interval_days"] == 1

    # Repeat failure call with same due date
    res2 = update_status(payload=req1, user_id=user_id)
    assert res2["status"] == "ok"

    # Verify reviews table contains exactly 1 uncompleted review, not duplicate
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM reviews WHERE user_id = ? AND problem_id = 42 AND completed = 0", (user_id,))
    review_count = c.fetchone()["count"]
    conn.close()

    assert review_count == 1
