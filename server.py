# server.py
import os
import json
import subprocess
import webbrowser
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database
from app.core.config import settings
from app.core.security import SecurityHeadersMiddleware, sanitize_title, sanitize_url
from app.core.protocol_engine import calculate_adaptive_budget, calculate_sm2_interval
from app.sheets import sheets_loader
from app.api.endpoints.badge import router as badge_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Enable CORS for browser extensions and public cloud hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Mount API Routers
app.include_router(badge_router, prefix="/api")

# Ensure DB is initialized
database.init_db()
database.migrate_json_to_sqlite()

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return default

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_current_user_id(authorization: Optional[str] = None, x_user: Optional[str] = None) -> int:
    token = None
    if authorization and isinstance(authorization, str) and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif x_user and isinstance(x_user, str) and len(x_user) == 64:
        token = x_user
    
    if token:
        user = database.get_user_by_token(token)
        if user:
            return user["id"]

    username = x_user if (isinstance(x_user, str) and x_user and len(x_user) != 64) else "local_user"
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, username))
    row = c.fetchone()
    if row:
        uid = row["id"]
        conn.close()
        return uid
    today_str = datetime.now().strftime("%Y-%m-%d")
    c.execute("""
    INSERT INTO users (username, email, password_hash, daily_goal, streak, last_active_date, today_solved_count, created_at)
    VALUES (?, ?, ?, 3, 1, ?, 0, ?)
    """, (username, f"{username}@anvilbreaker.is-a.dev", database.hash_password('default'), today_str, today_str))
    uid = c.lastrowid
    conn.commit()
    conn.close()
    return uid

# Detect browser executable path across platforms
def detect_browser_path(browser: str = "auto"):
    b = (browser or "auto").lower().strip()
    if b == "brave":
        for p in settings.BRAVE_PATHS:
            if os.path.exists(p):
                return p
    elif b == "chrome":
        for p in settings.CHROME_PATHS:
            if os.path.exists(p):
                return p
    elif b == "edge":
        for p in settings.EDGE_PATHS:
            if os.path.exists(p):
                return p
    elif b == "firefox":
        for p in getattr(settings, "FIREFOX_PATHS", []):
            if os.path.exists(p):
                return p
    elif b == "auto":
        for p_list in [settings.CHROME_PATHS, settings.BRAVE_PATHS, settings.EDGE_PATHS, getattr(settings, "FIREFOX_PATHS", [])]:
            for p in p_list:
                if os.path.exists(p):
                    return p
    return None

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ConnectAccountsRequest(BaseModel):
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    preferred_browser: Optional[str] = "auto"

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
    pace: Optional[str] = None
    brave_path: Optional[str] = None
    preferred_browser: Optional[str] = None
    auto_open_browser: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    current_problem_id: Optional[int] = None
    active_sheet: Optional[str] = None

class OpenBrowserRequest(BaseModel):
    problem_id: Optional[int] = None
    sheet_slug: Optional[str] = "core-path"
    url: Optional[str] = None
    browser: Optional[str] = "brave"

class CustomSheetCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    problems: List[Dict[str, Any]]

# Multi-Sheet Registry Endpoint
@app.get("/api/sheets")
def list_sheets(authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)

    system_sheets = [
        {
            "slug": "core-path",
            "title": "The Core Path (610 Problems)",
            "author": "Core Path Companion",
            "problem_count": 610,
            "description": "32 chapters, one problem per technique in optimal order",
            "is_system": True
        },
        {
            "slug": "striver-sde",
            "title": "Striver's SDE Sheet",
            "author": "take U forward",
            "problem_count": 95,
            "description": "The quintessential SDE interview preparation roadmap",
            "is_system": True
        },
        {
            "slug": "neetcode-150",
            "title": "NeetCode 150",
            "author": "NeetCode",
            "problem_count": 151,
            "description": "Curated 150 problems covering all foundational patterns",
            "is_system": True
        },
        {
            "slug": "blind-75",
            "title": "Blind 75",
            "author": "Yangshun Tay",
            "problem_count": 75,
            "description": "The high-yield 75 questions for rapid interview sprint",
            "is_system": True
        }
    ]

    custom_sheets = database.get_custom_sheets(user_id)
    formatted_custom = []
    for cs in custom_sheets:
        formatted_custom.append({
            "slug": cs["slug"],
            "title": cs["title"],
            "author": "Self-Made (You)",
            "problem_count": cs["problem_count"],
            "description": cs.get("description", "Custom user-curated sheet"),
            "is_system": False
        })

    return {
        "sheets": system_sheets + formatted_custom,
        "taxonomy": settings.ERROR_TAXONOMY
    }

# Get Specific Sheet & Problems
@app.get("/api/sheets/{slug}")
def get_sheet_details(slug: str, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)

    problems = []
    chapters = []

    if slug == "core-path":
        problems = load_json(os.path.join(settings.DATA_DIR, "problems.json"), [])
        chapters = load_json(os.path.join(settings.DATA_DIR, "chapters.json"), [])
    elif slug == "striver-sde":
        problems = sheets_loader.get_striver_sde_sheet()
        topics = list(dict.fromkeys([p["chapter_name"] for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p["chapter_name"] == t])} for i, t in enumerate(topics)]
    elif slug == "neetcode-150":
        problems = sheets_loader.get_neetcode_150_sheet()
        topics = list(dict.fromkeys([p.get("chapter_name", "General") for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p.get("chapter_name", "General") == t])} for i, t in enumerate(topics)]
    elif slug == "blind-75":
        problems = sheets_loader.get_blind_75_sheet()
        topics = list(dict.fromkeys([p.get("chapter_name", "General") for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p.get("chapter_name", "General") == t])} for i, t in enumerate(topics)]
    else:
        # Custom sheet
        custom = database.get_custom_sheet_by_slug(slug)
        if not custom:
            raise HTTPException(status_code=404, detail="Sheet not found")
        problems = custom.get("problems", [])
        topics = list(dict.fromkeys([p.get("chapter_name") or p.get("topic") or "General Practice" for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_name"] = p.get("chapter_name") or p.get("topic") or "General Practice"
            p["chapter_id"] = topic_to_id.get(p["chapter_name"], 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p["chapter_name"] == t])} for i, t in enumerate(topics)]

    # Fetch User Progress from DB
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(c.fetchone())

    today_str = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
    progress_map = {}
    for row in c.fetchall():
        r = dict(row)
        progress_map[str(r["problem_id"])] = {
            "status": r["status"],
            "time_spent": r["time_spent"],
            "pattern": r["pattern"],
            "error_type": r["error_type"],
            "error_note": r["error_note"],
            "scratchpad": r["scratchpad"],
            "solved_at": r["solved_at"]
        }

    c.execute("SELECT * FROM reviews WHERE user_id = ? AND completed = 0 AND due_date <= ?", (user_id, today_str))
    due_reviews = []
    prob_map = {p["id"]: p for p in problems}
    for row in c.fetchall():
        r = dict(row)
        pid = r["problem_id"]
        if pid in prob_map:
            due_reviews.append({
                "problem_id": pid,
                "title": prob_map[pid]["title"],
                "chapter": prob_map[pid].get("chapter_name", "DSA"),
                "due_date": r["due_date"],
                "interval_type": r["review_type"],
                "level": prob_map[pid].get("level", "M")
            })
    conn.close()

    return {
        "sheet_slug": slug,
        "problems": problems,
        "chapters": chapters,
        "progress": {
            "daily_goal": user.get("daily_goal", 3),
            "streak": user.get("streak", 1),
            "today_solved_count": user.get("today_solved_count", 0),
            "current_problem_id": user.get("current_problem_id", 1),
            "active_sheet": user.get("active_sheet", slug),
            "brave_path": user.get("brave_path") or detect_browser_path("brave"),
            "sound_enabled": bool(user.get("sound_enabled", 1)),
            "problems": progress_map
        },
        "due_reviews": due_reviews,
        "brave_available": os.path.exists(detect_browser_path("brave") or ""),
        "preferred_browser": user.get("preferred_browser") or "auto",
        "github_username": user.get("github_username") or "",
        "leetcode_username": user.get("leetcode_username") or ""
    }

# ==================== AUTHENTICATION & CONNECTED ACCOUNTS ====================

@app.post("/api/auth/register")
def auth_register(payload: RegisterRequest):
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if not payload.password or len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    user, err = database.register_user(email=email, password=payload.password, username=payload.username)
    if err:
        raise HTTPException(status_code=400, detail=err)
    
    return {
        "status": "ok",
        "token": user["session_token"],
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "github_username": user.get("github_username") or "",
            "leetcode_username": user.get("leetcode_username") or "",
            "preferred_browser": user.get("preferred_browser") or "auto"
        }
    }

@app.post("/api/auth/login")
def auth_login(payload: LoginRequest):
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not payload.password:
        raise HTTPException(status_code=400, detail="Password is required")
        
    user, err = database.authenticate_user(email, payload.password)
    if err or not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    return {
        "status": "ok",
        "token": user["session_token"],
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "github_username": user.get("github_username") or "",
            "leetcode_username": user.get("leetcode_username") or "",
            "preferred_browser": user.get("preferred_browser") or "auto"
        }
    }

@app.get("/api/auth/me")
def auth_me(authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    user = database.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "ok",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email") or f"{user['username']}@anvilbreaker.is-a.dev",
            "github_username": user.get("github_username") or "",
            "leetcode_username": user.get("leetcode_username") or "",
            "preferred_browser": user.get("preferred_browser") or "auto",
            "daily_goal": user.get("daily_goal", 3),
            "streak": user.get("streak", 1),
            "active_sheet": user.get("active_sheet", "core-path")
        }
    }

@app.post("/api/auth/connect")
def auth_connect(payload: ConnectAccountsRequest, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    updated_user = database.update_user_connections(
        user_id=user_id,
        github_username=payload.github_username,
        leetcode_username=payload.leetcode_username,
        preferred_browser=payload.preferred_browser
    )
    return {
        "status": "ok",
        "user": {
            "id": updated_user["id"],
            "username": updated_user["username"],
            "email": updated_user.get("email") or f"{updated_user['username']}@anvilbreaker.is-a.dev",
            "github_username": updated_user.get("github_username") or "",
            "leetcode_username": updated_user.get("leetcode_username") or "",
            "preferred_browser": updated_user.get("preferred_browser") or "auto"
        }
    }

# Initialization endpoint
@app.get("/api/init")
def api_init(authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT active_sheet FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    active_sheet = "core-path"
    if row and row["active_sheet"]:
        active_sheet = row["active_sheet"]
    conn.close()
    return get_sheet_details(active_sheet, authorization, x_user)

# Create / Import Custom Self-Made Sheet
@app.post("/api/sheets/custom")
def create_custom_sheet(payload: CustomSheetCreateRequest, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)

    title = sanitize_title(payload.title)
    if not title:
        raise HTTPException(status_code=400, detail="Sheet title is required")

    slug = sheets_loader.slugify(title)
    if not slug:
        slug = f"sheet-{int(datetime.now().timestamp())}"

    # Format problems cleanly
    formatted_problems = []
    for idx, p in enumerate(payload.problems, 1):
        p_title = sanitize_title(p.get("title", f"Problem {idx}"))
        p_url = sanitize_url(p.get("url", f"https://leetcode.com/problems/{sheets_loader.slugify(p_title)}/"))
        p_lvl = p.get("level", "M").upper()
        if p_lvl not in ["E", "M", "H"]:
            p_lvl = "M"
        
        formatted_problems.append({
            "id": idx,
            "title": p_title,
            "chapter_name": p.get("topic") or p.get("chapter_name") or "General Practice",
            "level": p_lvl,
            "level_full": "Easy" if p_lvl == "E" else ("Medium" if p_lvl == "M" else "Hard"),
            "lists": ["Custom"],
            "hint": p.get("hint") or "Custom problem entry",
            "platform": "LeetCode" if "leetcode" in p_url else "Web",
            "url": p_url,
            "is_premium": False
        })

    database.save_custom_sheet(user_id, slug, title, payload.description or "", formatted_problems)
    return {"status": "ok", "slug": slug, "count": len(formatted_problems)}

# Delete Custom Sheet
@app.delete("/api/sheets/custom/{slug}")
def delete_custom_sheet(slug: str, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    database.delete_custom_sheet(user_id, slug)
    return {"status": "ok", "deleted": slug}

# Global Platform Statistics (Anvil Breaker Network)
@app.get("/api/stats/platform")
def get_global_platform_stats():
    return {
        "status": "ok",
        "brand": settings.PROJECT_NAME,
        "founder": settings.FOUNDER,
        "version": settings.VERSION,
        "metrics": database.get_platform_stats()
    }

# Adaptive Protocol Calculation Endpoint (Defensible Moat)
@app.get("/api/protocol/adaptive")
def get_adaptive_protocol(difficulty: str = "M", topic: str = "General"):
    budget = calculate_adaptive_budget(difficulty, user_fail_rate_topic=0.0)
    return budget

# Status Update with SM-2 Memory Engine
@app.post("/api/progress/status")
def update_status(payload: StatusUpdateRequest, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    today_str = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = database.get_connection()
    c = conn.cursor()

    c.execute("SELECT status FROM user_progress WHERE user_id = ? AND problem_id = ?", (user_id, payload.problem_id))
    old_row = c.fetchone()
    old_status = old_row["status"] if old_row else "unsolved"

    c.execute("""
    INSERT INTO user_progress (user_id, problem_id, status, time_spent, pattern, error_type, error_note, scratchpad, solved_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id, problem_id) DO UPDATE SET
        status = excluded.status,
        time_spent = excluded.time_spent,
        pattern = coalesce(nullif(excluded.pattern, ''), user_progress.pattern),
        error_type = coalesce(nullif(excluded.error_type, ''), user_progress.error_type),
        error_note = coalesce(nullif(excluded.error_note, ''), user_progress.error_note),
        scratchpad = coalesce(excluded.scratchpad, user_progress.scratchpad),
        solved_at = coalesce(excluded.solved_at, user_progress.solved_at),
        updated_at = excluded.updated_at
    """, (
        user_id,
        payload.problem_id,
        payload.status,
        payload.time_spent,
        payload.pattern or "",
        payload.error_type or "",
        payload.error_note or "",
        payload.scratchpad,
        today_str if payload.status in ["clean", "help"] else None,
        now_str
    ))

    # Update streak & today count
    if payload.status in ["clean", "help"] and old_status not in ["clean", "help"]:
        c.execute("""
        UPDATE users SET today_solved_count = today_solved_count + 1, streak = max(streak, 1)
        WHERE id = ?
        """, (user_id,))

    # Calculate SM-2 interval
    quality = 5 if payload.status == "clean" else (2 if payload.status == "help" else 1)
    sm2 = calculate_sm2_interval(quality=quality, repetitions=0, ef=2.5, prev_interval=1)

    if payload.status in ["help", "failed"]:
        c.execute("""
        INSERT INTO reviews (user_id, problem_id, review_type, due_date, completed, created_at)
        VALUES (?, ?, ?, ?, 0, ?)
        """, (user_id, payload.problem_id, f"SM-2 Spaced Re-Solve (Interval: {sm2['interval_days']}d)", sm2["due_date"], now_str))

    conn.commit()
    conn.close()

    return {"status": "ok", "problem_id": payload.problem_id, "sm2": sm2}

# Notes Auto-save
@app.post("/api/progress/notes")
def update_notes(payload: NotesUpdateRequest, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = database.get_connection()
    c = conn.cursor()
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

# Launch Browser Dynamically (Brave, Chrome, Edge, Firefox, or System Default)
@app.post("/api/open-browser")
def open_browser_endpoint(payload: OpenBrowserRequest):
    url = payload.url
    if not url:
        raise HTTPException(status_code=400, detail="Target URL required")

    chosen_browser = payload.browser or "auto"
    browser_exe = detect_browser_path(chosen_browser)
    is_cloud = bool(os.getenv("RENDER") or os.getenv("PORT") or os.name != "nt")

    launched_direct = False
    if not is_cloud and browser_exe and os.path.exists(browser_exe):
        try:
            subprocess.Popen([browser_exe, url], shell=False)
            launched_direct = True
        except Exception as e:
            print(f"Failed to launch {chosen_browser} directly: {e}")

    if not is_cloud and not launched_direct:
        try:
            webbrowser.open(url)
            launched_direct = True
        except Exception as e:
            pass

    return {
        "status": "ok",
        "url": url,
        "browser": chosen_browser,
        "is_cloud": is_cloud,
        "launched_direct": launched_direct,
        "browser_path": browser_exe
    }

# Update Settings
@app.post("/api/settings")
def update_settings(payload: SettingsUpdateRequest, authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
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

# Export Progress Backup
@app.get("/api/export")
def export_backup(authorization: Optional[str] = Header(None), x_user: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user)
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(c.fetchone())
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
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=dsa_backup_{username}_{datetime.now().strftime('%Y%m%d')}.json"}
    )

# Backward-compatible endpoint
@app.post("/api/open-brave")
def open_in_brave_legacy(payload: OpenBrowserRequest):
    payload.browser = "brave"
    return open_browser_endpoint(payload)

# Serve Frontend
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Official Home Page & Landing (Dynamic Sign Up / Sign In Vault)
@app.get("/")
@app.get("/home")
@app.get("/welcome")
@app.get("/landing")
@app.get("/login")
@app.get("/register")
@app.get("/signup")
def serve_home():
    landing_file = os.path.join(settings.STATIC_DIR, "landing.html")
    if os.path.exists(landing_file):
        return FileResponse(landing_file)
    return FileResponse(os.path.join(settings.STATIC_DIR, "index.html"))

# Private Workspace Command Center (Authenticated Personal Vault)
@app.get("/app")
@app.get("/workspace")
@app.get("/solver")
@app.get("/dashboard")
def serve_app():
    index_file = os.path.join(settings.STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": f"{settings.PROJECT_NAME} API Ready"})

# Floating Pop-Up Mini HUD Endpoint
@app.get("/mini-hud")
@app.get("/mini")
def serve_mini_hud():
    mini_file = os.path.join(settings.STATIC_DIR, "mini.html")
    if os.path.exists(mini_file):
        return FileResponse(mini_file)
    return FileResponse(os.path.join(settings.STATIC_DIR, "index.html"))

# Cloud Health Check Endpoint (Render, Railway, Fly.io, Kubernetes)
@app.get("/healthz")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "domain": settings.DOMAIN,
        "base_url": settings.BASE_URL,
        "founder": settings.FOUNDER,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8765))
    print(f"Starting {settings.PROJECT_NAME} on http://{host}:{port}")
    uvicorn.run("server:app", host=host, port=port, log_level="info")
