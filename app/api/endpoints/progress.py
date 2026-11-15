# app/api/endpoints/progress.py
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import database
from app.core.config import settings
from app.core.dependencies import get_authenticated_user_id, get_optional_user_id
from app.core.protocol_engine import calculate_adaptive_budget, calculate_sm2_interval
from app.sheets import sheets_loader

router = APIRouter(tags=["progress"])

class StatusUpdateRequest(BaseModel):
    problem_id: int
    sheet_slug: Optional[str] = "core-path"
    status: str  # "clean", "help", "failed", "unsolved"
    time_spent: Optional[int] = 0
    pattern: Optional[str] = ""
    error_type: Optional[str] = ""  # "idea", "proof", "boundary", "speed", "gotcha"
    error_note: Optional[str] = ""
    scratchpad: Optional[str] = None
    sm2_quality: Optional[int] = 4

class NotesUpdateRequest(BaseModel):
    problem_id: int
    scratchpad: str

class SettingsUpdateRequest(BaseModel):
    daily_goal: Optional[int] = None
    brave_path: Optional[str] = None
    preferred_browser: Optional[str] = None
    sound_enabled: Optional[bool] = None
    current_problem_id: Optional[int] = None
    active_sheet: Optional[str] = None

class CompleteReviewRequest(BaseModel):
    review_id: int

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return default

@router.get("/init")
def api_init(user_id: int = Depends(get_optional_user_id)):
    """
    Returns initial core dataset, user progress map, settings, and streak stats.
    """
    problems = load_json(os.path.join(settings.DATA_DIR, "problems.json"), [])
    chapters = load_json(os.path.join(settings.DATA_DIR, "chapters.json"), [])
    rules = load_json(os.path.join(settings.DATA_DIR, "rules.json"), [])

    conn = database.get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = c.fetchone()
    if not user_row:
        user_row = {
            "id": user_id, "username": "local_user", "daily_goal": 3,
            "streak": 1, "today_solved_count": 0, "active_sheet": "core-path",
            "sound_enabled": 1, "current_problem_id": 1
        }
    user = dict(user_row)
    user.pop("password_hash", None)
    user.pop("session_token", None)

    c.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
    progress_rows = c.fetchall()
    progress_dict = {}
    for r in progress_rows:
        progress_dict[str(r["problem_id"])] = {
            "status": r["status"],
            "time_spent": r["time_spent"],
            "pattern": r["pattern"],
            "error_type": r["error_type"],
            "error_note": r["error_note"],
            "scratchpad": r["scratchpad"],
            "solved_at": r["solved_at"],
            "repetitions": r["repetitions"],
            "easiness_factor": r["easiness_factor"],
            "interval_days": r["interval_days"],
            "due_date": r["due_date"]
        }

    c.execute("SELECT * FROM reviews WHERE user_id = ? AND completed = 0 ORDER BY due_date ASC", (user_id,))
    reviews = [dict(r) for r in c.fetchall()]
    conn.close()

    return {
        "problems": problems,
        "chapters": chapters,
        "rules": rules,
        "user": user,
        "progress": progress_dict,
        "reviews": reviews,
        "taxonomy": settings.ERROR_TAXONOMY
    }

@router.post("/progress/status")
def update_status(
    payload: StatusUpdateRequest,
    user_id: int = Depends(get_authenticated_user_id)
):
    """
    Records solve/fail attempt.
    Phase 2 Protocol Engine:
    1. Advances user streak from last_active_date.
    2. Persists SM-2 parameters (repetitions, easiness_factor, interval_days, due_date).
    3. Prevents duplicate review rows for the same problem and due date.
    """
    conn = database.get_connection()
    c = conn.cursor()

    now_dt = datetime.now()
    today_str = now_dt.strftime("%Y-%m-%d")
    yesterday_str = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    # 1. Advance Streak from last_active_date
    c.execute("SELECT streak, last_active_date, today_solved_count FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    current_streak = user_data["streak"] or 1 if user_data else 1
    last_active = user_data["last_active_date"] if user_data else None
    today_solved = user_data["today_solved_count"] or 0 if user_data else 0

    if payload.status in ("clean", "help"):
        if last_active == today_str:
            today_solved += 1
        elif last_active == yesterday_str:
            current_streak += 1
            today_solved = 1
            last_active = today_str
        else:
            current_streak = 1
            today_solved = 1
            last_active = today_str

        c.execute("""
        UPDATE users 
        SET streak = ?, last_active_date = ?, today_solved_count = ?
        WHERE id = ?
        """, (current_streak, last_active, today_solved, user_id))

    # 2. Retrieve previous SM-2 parameters for accurate calculation
    c.execute("""
    SELECT repetitions, easiness_factor, interval_days 
    FROM user_progress 
    WHERE user_id = ? AND problem_id = ?
    """, (user_id, payload.problem_id))
    existing_prog = c.fetchone()

    prev_reps = existing_prog["repetitions"] if (existing_prog and existing_prog["repetitions"] is not None) else 0
    prev_ef = existing_prog["easiness_factor"] if (existing_prog and existing_prog["easiness_factor"] is not None) else 2.5
    prev_interval = existing_prog["interval_days"] if (existing_prog and existing_prog["interval_days"] is not None) else 1

    quality = payload.sm2_quality if payload.sm2_quality is not None else (4 if payload.status == "clean" else 2)
    sm2 = calculate_sm2_interval(
        quality=quality,
        repetitions=prev_reps,
        ef=prev_ef,
        prev_interval=prev_interval
    )

    # Persist progress with updated SM-2 retention metrics
    c.execute("""
    INSERT INTO user_progress (
        user_id, problem_id, status, time_spent, pattern, 
        error_type, error_note, scratchpad, solved_at, updated_at,
        repetitions, easiness_factor, interval_days, due_date
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id, problem_id) DO UPDATE SET
        status = excluded.status,
        time_spent = excluded.time_spent,
        pattern = excluded.pattern,
        error_type = excluded.error_type,
        error_note = excluded.error_note,
        scratchpad = COALESCE(excluded.scratchpad, user_progress.scratchpad),
        solved_at = excluded.solved_at,
        updated_at = excluded.updated_at,
        repetitions = excluded.repetitions,
        easiness_factor = excluded.easiness_factor,
        interval_days = excluded.interval_days,
        due_date = excluded.due_date
    """, (
        user_id, payload.problem_id, payload.status, payload.time_spent,
        payload.pattern, payload.error_type, payload.error_note,
        payload.scratchpad, now_str if payload.status in ("clean", "help") else None, now_str,
        sm2["repetitions"], sm2["easiness_factor"], sm2["interval_days"], sm2["due_date"]
    ))

    # 3. Schedule SM-2 Spaced Repetition Review (Skipping Duplicates)
    if payload.status == "failed" or quality < 3:
        review_due = sm2["due_date"]
        c.execute("""
        SELECT id FROM reviews 
        WHERE user_id = ? AND problem_id = ? AND due_date = ? AND completed = 0
        """, (user_id, payload.problem_id, review_due))
        existing_review = c.fetchone()

        if not existing_review:
            c.execute("""
            INSERT INTO reviews (user_id, problem_id, review_type, due_date, completed, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
            """, (user_id, payload.problem_id, "Failure Stand-Down" if payload.status == "failed" else "Editorial Review", review_due, now_str))

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "sm2": sm2,
        "streak": current_streak,
        "today_solved": today_solved
    }

@router.post("/progress/notes")
def update_notes(
    payload: NotesUpdateRequest,
    user_id: int = Depends(get_authenticated_user_id)
):
    """Updates scratchpad notes for a problem."""
    conn = database.get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO user_progress (user_id, problem_id, status, scratchpad, updated_at)
    VALUES (?, ?, 'unsolved', ?, ?)
    ON CONFLICT(user_id, problem_id) DO UPDATE SET
        scratchpad = excluded.scratchpad,
        updated_at = excluded.updated_at
    """, (user_id, payload.problem_id, payload.scratchpad, now_str))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@router.get("/progress/reviews")
def get_reviews(user_id: int = Depends(get_optional_user_id)):
    """Returns active spaced repetition reviews."""
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT * FROM reviews 
    WHERE user_id = ? AND completed = 0 
    ORDER BY due_date ASC
    """, (user_id,))
    reviews = [dict(row) for row in c.fetchall()]
    conn.close()

    problems = load_json(os.path.join(settings.DATA_DIR, "problems.json"), [])
    prob_map = {p["id"]: p for p in problems}
    for r in reviews:
        p = prob_map.get(r["problem_id"])
        if p:
            r["problem_title"] = p.get("title", f"Problem #{r['problem_id']}")
            r["difficulty"] = p.get("difficulty", "M")
            r["chapter_name"] = p.get("chapter_name", "General")
        else:
            r["problem_title"] = f"Problem #{r['problem_id']}"
            r["difficulty"] = "M"
            r["chapter_name"] = "General"

    return {"status": "ok", "reviews": reviews}

@router.post("/progress/reviews/complete")
def complete_review(
    payload: CompleteReviewRequest,
    user_id: int = Depends(get_authenticated_user_id)
):
    """Marks a spaced repetition review as completed."""
    conn = database.get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    UPDATE reviews 
    SET completed = 1, completed_at = ? 
    WHERE id = ? AND user_id = ?
    """, (now_str, payload.review_id, user_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@router.post("/progress/reset")
def reset_progress(user_id: int = Depends(get_authenticated_user_id)):
    """Resets user progress and review queue."""
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM user_progress WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM reviews WHERE user_id = ?", (user_id,))
    c.execute("UPDATE users SET today_solved_count = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Progress reset"}

@router.post("/settings")
def update_settings(
    payload: SettingsUpdateRequest,
    user_id: int = Depends(get_authenticated_user_id)
):
    """Updates user preferences and active sheet."""
    conn = database.get_connection()
    c = conn.cursor()
    if payload.daily_goal is not None:
        c.execute("UPDATE users SET daily_goal = ? WHERE id = ?", (payload.daily_goal, user_id))
    if payload.brave_path is not None:
        c.execute("UPDATE users SET brave_path = ? WHERE id = ?", (payload.brave_path, user_id))
    if payload.preferred_browser is not None:
        c.execute("UPDATE users SET preferred_browser = ? WHERE id = ?", (payload.preferred_browser, user_id))
    if payload.current_problem_id is not None:
        c.execute("UPDATE users SET current_problem_id = ? WHERE id = ?", (payload.current_problem_id, user_id))
    if payload.active_sheet is not None:
        c.execute("UPDATE users SET active_sheet = ? WHERE id = ?", (payload.active_sheet, user_id))
    if payload.sound_enabled is not None:
        c.execute("UPDATE users SET sound_enabled = ? WHERE id = ?", (1 if payload.sound_enabled else 0, user_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@router.get("/protocol/budget")
def get_adaptive_budget(
    difficulty: str = "M",
    topic: Optional[str] = None,
    user_id: int = Depends(get_optional_user_id)
):
    """
    Computes 4-phase timebox allocations calibrated against the user's real topic fail rate.
    """
    user_fail_rate = 0.0

    if topic:
        conn = database.get_connection()
        c = conn.cursor()
        # Find problems in topic from problems.json or matching pattern
        problems = load_json(os.path.join(settings.DATA_DIR, "problems.json"), [])
        topic_prob_ids = [p["id"] for p in problems if p.get("chapter_name", "").lower() == topic.lower()]

        if topic_prob_ids:
            placeholders = ",".join(["?"] * len(topic_prob_ids))
            c.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM user_progress 
            WHERE user_id = ? AND problem_id IN ({placeholders})
            """, [user_id] + topic_prob_ids)
            row = c.fetchone()
            if row and row["total"] and row["total"] > 0:
                user_fail_rate = (row["failed"] or 0) / row["total"]
        conn.close()

    budget = calculate_adaptive_budget(difficulty=difficulty, user_fail_rate_topic=user_fail_rate)
    budget["user_fail_rate_topic"] = round(user_fail_rate, 2)
    return budget

@router.get("/export")
def export_backup(user_id: int = Depends(get_authenticated_user_id)):
    """
    Exports clean encrypted/scrubbed backup of user data.
    Security Gate: password_hash and session_token are strictly stripped.
    Header filename uses real user username.
    """
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = c.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    user = dict(user_row)
    # Strictly strip security credentials
    user.pop("password_hash", None)
    user.pop("session_token", None)

    c.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
    progress = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM reviews WHERE user_id = ?", (user_id,))
    reviews = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM custom_sheets WHERE user_id = ?", (user_id,))
    sheets = [dict(r) for r in c.fetchall()]
    conn.close()

    data = {
        "user": user,
        "progress": progress,
        "reviews": reviews,
        "custom_sheets": sheets,
        "exported_at": datetime.now().isoformat()
    }

    username = user.get("username") or "user"
    filename = f"dsa_backup_{username}_{datetime.now().strftime('%Y%m%d')}.json"

    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
