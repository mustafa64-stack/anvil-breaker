# database.py
import sqlite3
import os
import json
from datetime import datetime, timedelta
import hashlib
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
DB_PATH = os.path.join(DATA_DIR, "dsa_app.db")

def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # High-throughput concurrency optimizations (WAL Mode for 100k+ users)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

# Slow PBKDF2 Password Hashing with 100,000 iterations & unique random salt
def hash_password(password: str, salt: str = None) -> str:
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256:100000${salt}${key.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    if not stored_hash or not password:
        return False
    if stored_hash.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_hash.split("$")
            salt = parts[1]
            expected_hex = parts[2]
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return secrets.compare_digest(key.hex(), expected_hex)
        except Exception:
            return False
    # Backward compatibility with legacy SHA-256
    legacy = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return secrets.compare_digest(stored_hash, legacy)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        daily_goal INTEGER DEFAULT 3,
        streak INTEGER DEFAULT 1,
        last_active_date TEXT,
        today_solved_count INTEGER DEFAULT 0,
        brave_path TEXT,
        current_problem_id INTEGER DEFAULT 1,
        active_sheet TEXT DEFAULT 'core-path',
        sound_enabled INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)

    # Ensure optional columns exist if table was previously created
    for col_name, col_type in [
        ("current_problem_id", "INTEGER DEFAULT 1"),
        ("active_sheet", "TEXT DEFAULT 'core-path'"),
        ("sound_enabled", "INTEGER DEFAULT 1"),
        ("brave_path", "TEXT"),
        ("email", "TEXT"),
        ("github_username", "TEXT"),
        ("leetcode_username", "TEXT"),
        ("preferred_browser", "TEXT DEFAULT 'auto'"),
        ("session_token", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # User Progress Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'clean', 'help', 'failed', 'unsolved'
        time_spent INTEGER DEFAULT 0,
        pattern TEXT,
        error_type TEXT, -- 'idea', 'proof', 'bug', 'speed'
        error_note TEXT,
        scratchpad TEXT,
        solved_at TEXT,
        updated_at TEXT,
        UNIQUE(user_id, problem_id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Spaced Repetition Reviews Table (Rules 3 & 4)
    c.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        review_type TEXT NOT NULL,
        due_date TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        completed_at TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Custom Sheets Table (Self-Made Sheets by users)
    c.execute("""
    CREATE TABLE IF NOT EXISTS custom_sheets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        problem_count INTEGER DEFAULT 0,
        problems_json TEXT NOT NULL,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Ensure optional columns exist if user_progress was previously created
    for col_name, col_type in [
        ("repetitions", "INTEGER DEFAULT 0"),
        ("easiness_factor", "REAL DEFAULT 2.5"),
        ("interval_days", "INTEGER DEFAULT 1"),
        ("due_date", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE user_progress ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # System Metadata & One-Time Migration Tracking Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS _system_meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Default / Local user creation
    c.execute("SELECT id FROM users WHERE username = 'local_user'")
    row = c.fetchone()
    if not row:
        today_str = datetime.now().strftime("%Y-%m-%d")
        c.execute("""
        INSERT INTO users (username, password_hash, daily_goal, streak, last_active_date, today_solved_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('local_user', hash_password('local_dev_pass'), 3, 1, today_str, 0, today_str))

    conn.commit()
    conn.close()

# Migration helper from user_progress.json - Runs safely exactly once
def migrate_json_to_sqlite():
    conn = get_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS _system_meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("SELECT value FROM _system_meta WHERE key = 'json_migrated'")
    if c.fetchone():
        conn.close()
        return

    json_path = os.path.join(DATA_DIR, "user_progress.json")
    if not os.path.exists(json_path):
        c.execute("INSERT OR REPLACE INTO _system_meta (key, value) VALUES ('json_migrated', '1')")
        conn.commit()
        conn.close()
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        c.execute("SELECT id FROM users WHERE username = 'local_user'")
        u = c.fetchone()
        if not u:
            conn.close()
            return
        user_id = u["id"]

        # Update user meta
        c.execute("""
        UPDATE users SET daily_goal = ?, streak = ?, last_active_date = ?, today_solved_count = ?, brave_path = ?
        WHERE id = ?
        """, (
            data.get("daily_goal", 3),
            data.get("streak", 1),
            data.get("last_active_date", datetime.now().strftime("%Y-%m-%d")),
            data.get("today_solved_count", 0),
            data.get("brave_path"),
            user_id
        ))

        # Migrate problems
        problems_dict = data.get("problems", {})
        for pid_str, pdata in problems_dict.items():
            pid = int(pid_str)
            c.execute("""
            INSERT OR REPLACE INTO user_progress 
            (user_id, problem_id, status, time_spent, pattern, error_type, error_note, scratchpad, solved_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                pid,
                pdata.get("status", "unsolved"),
                pdata.get("time_spent", 0),
                pdata.get("pattern", ""),
                pdata.get("error_type", ""),
                pdata.get("error_note", ""),
                pdata.get("scratchpad", ""),
                pdata.get("solved_at"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            # Migrate reviews
            reviews = pdata.get("reviews", [])
            for r in reviews:
                c.execute("""
                INSERT INTO reviews (user_id, problem_id, review_type, due_date, completed, completed_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    pid,
                    r.get("type", "Review"),
                    r.get("due_date", datetime.now().strftime("%Y-%m-%d")),
                    1 if r.get("completed") else 0,
                    r.get("completed_at"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

        c.execute("INSERT OR REPLACE INTO _system_meta (key, value) VALUES ('json_migrated', '1')")
        conn.commit()
        conn.close()
        print("Successfully migrated user_progress.json to SQLite database (one-time)!")
    except Exception as e:
        conn.close()
        print(f"Error migrating JSON to SQLite: {e}")

def save_custom_sheet(user_id: int, slug: str, title: str, description: str, problems: list):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO custom_sheets (user_id, slug, title, description, problem_count, problems_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(slug) DO UPDATE SET
        title = excluded.title,
        description = excluded.description,
        problem_count = excluded.problem_count,
        problems_json = excluded.problems_json
    """, (user_id, slug, title, description, len(problems), json.dumps(problems, ensure_ascii=False), now_str))
    conn.commit()
    conn.close()

def get_custom_sheets(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, slug, title, description, problem_count, created_at FROM custom_sheets WHERE user_id = ?", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_custom_sheet_by_slug(slug: str, user_id: int = None):
    conn = get_connection()
    c = conn.cursor()
    if user_id is not None:
        c.execute("SELECT * FROM custom_sheets WHERE slug = ? AND user_id = ?", (slug, user_id))
    else:
        c.execute("SELECT * FROM custom_sheets WHERE slug = ?", (slug,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["problems"] = json.loads(d["problems_json"])
        return d
    return None

def delete_custom_sheet(user_id: int, slug: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM custom_sheets WHERE user_id = ? AND slug = ?", (user_id, slug))
    conn.commit()
    conn.close()

def register_user(email: str, password: str, username: str = None):
    conn = get_connection()
    c = conn.cursor()
    email_clean = email.strip().lower()
    if not username:
        username = email_clean.split('@')[0]
    
    # Check if user already exists
    c.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email_clean, username))
    if c.fetchone():
        conn.close()
        return None, "User with this email or username already exists"

    today_str = datetime.now().strftime("%Y-%m-%d")
    pwd_hash = hash_password(password)
    # Generate cryptographically secure 256-bit session token
    token = secrets.token_hex(32)

    c.execute("""
    INSERT INTO users (username, email, password_hash, session_token, daily_goal, streak, last_active_date, today_solved_count, created_at)
    VALUES (?, ?, ?, ?, 3, 1, ?, 0, ?)
    """, (username, email_clean, pwd_hash, token, today_str, today_str))
    
    user_id = c.lastrowid
    conn.commit()
    
    c.execute("SELECT id, username, email, github_username, leetcode_username, preferred_browser, session_token FROM users WHERE id = ?", (user_id,))
    row = dict(c.fetchone())
    conn.close()
    return row, None

def authenticate_user(email_or_username: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    clean_identifier = email_or_username.strip().lower()

    c.execute("SELECT * FROM users WHERE email = ? OR username = ?", (clean_identifier, clean_identifier))
    user_row = c.fetchone()
    if not user_row:
        conn.close()
        return None, "Invalid email or password"

    user = dict(user_row)
    if not verify_password(user["password_hash"], password):
        conn.close()
        return None, "Invalid email or password"

    # Automatically upgrade legacy unsalted SHA-256 hashes to PBKDF2
    if not user["password_hash"].startswith("pbkdf2:sha256:"):
        new_hash = hash_password(password)
        c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user['id']))

    # Refresh cryptographically secure session token
    token = secrets.token_hex(32)
    c.execute("UPDATE users SET session_token = ? WHERE id = ?", (token, user['id']))
    conn.commit()
    user["session_token"] = token
    conn.close()
    return user, None

def get_user_by_token(token: str):
    if not token:
        return None
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, email, github_username, leetcode_username, preferred_browser, daily_goal, streak, active_sheet FROM users WHERE session_token = ?", (token,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, email, github_username, leetcode_username, preferred_browser, daily_goal, streak, active_sheet FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_connections(user_id: int, github_username: str = None, leetcode_username: str = None, preferred_browser: str = None):
    conn = get_connection()
    c = conn.cursor()
    if github_username is not None:
        c.execute("UPDATE users SET github_username = ? WHERE id = ?", (github_username.strip(), user_id))
    if leetcode_username is not None:
        c.execute("UPDATE users SET leetcode_username = ? WHERE id = ?", (leetcode_username.strip(), user_id))
    if preferred_browser is not None:
        c.execute("UPDATE users SET preferred_browser = ? WHERE id = ?", (preferred_browser.strip(), user_id))
    conn.commit()
    c.execute("SELECT id, username, email, github_username, leetcode_username, preferred_browser, daily_goal, streak, active_sheet FROM users WHERE id = ?", (user_id,))
    row = dict(c.fetchone())
    conn.close()
    return row

def get_platform_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM users")
    total_users = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) as count FROM user_progress WHERE status IN ('clean', 'help')")
    total_solves = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) as count FROM reviews WHERE completed = 1")
    completed_reviews = c.fetchone()["count"]

    c.execute("SELECT error_type, COUNT(*) as count FROM user_progress WHERE error_type != '' GROUP BY error_type")
    error_stats = {r["error_type"]: r["count"] for r in c.fetchall()}

    c.execute("SELECT MAX(streak) as max_streak FROM users")
    top_streak = c.fetchone()["max_streak"] or 1

    conn.close()
    return {
        "total_users": max(1, total_users),
        "total_solves": total_solves,
        "completed_reviews": completed_reviews,
        "top_streak": top_streak,
        "error_distribution": error_stats
    }

if __name__ == "__main__":
    init_db()
    migrate_json_to_sqlite()
    print("Database initialized successfully at", DB_PATH)

