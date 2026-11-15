# One-shot generator for the six phase work packets. Not part of the app.
from fpdf import FPDF
from pathlib import Path

OUT = Path(__file__).resolve().parent


class Packet(FPDF):
    def __init__(self, kicker, footer):
        super().__init__(format="A4")
        self.kicker = kicker
        self.footer_label = footer
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(16, 18, 16)

    def header(self):
        self.set_fill_color(24, 24, 27)
        self.rect(0, 0, 210, 11, "F")
        self.set_xy(16, 2.5)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(245, 158, 11)
        self.cell(0, 6, self.kicker, align="L")
        self.set_text_color(228, 228, 231)
        self.set_xy(16, 2.5)
        self.cell(0, 6, "Anvil Breaker  |  path to 10", align="R")

    def footer(self):
        self.set_y(-12)
        self.set_draw_color(212, 212, 216)
        self.line(16, self.get_y(), 194, self.get_y())
        self.set_y(-10)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(113, 113, 122)
        self.cell(0, 6, f"{self.footer_label}    {self.page_no()}", align="R")

    def gap(self, h=2):
        self.ln(h)

    def h1(self, text):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(24, 24, 27)
        self.multi_cell(0, 8, text)
        self.gap(1)

    def lede(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(63, 63, 70)
        self.multi_cell(0, 5.6, text)
        self.gap(2)

    def h2(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.gap(2)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(24, 24, 27)
        self.multi_cell(0, 6.5, text)
        y = self.get_y()
        self.set_draw_color(245, 158, 11)
        self.set_line_width(0.45)
        self.line(16, y, 52, y)
        self.gap(3)

    def h3(self, text):
        if self.get_y() > 260:
            self.add_page()
        self.gap(1)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(63, 63, 70)
        self.multi_cell(0, 5.6, text)
        self.gap(1)

    def p(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(39, 39, 42)
        self.multi_cell(0, 5.2, text)
        self.gap(1.4)

    def bullet(self, text, mark="-"):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(39, 39, 42)
        self.multi_cell(0, 5.2, f"{mark}  {text}")
        self.gap(0.6)

    def meta(self, rows):
        self.set_fill_color(250, 250, 250)
        self.set_draw_color(228, 228, 231)
        for label, value in rows:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(113, 113, 122)
            self.cell(36, 7, label, border=0)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(24, 24, 27)
            self.multi_cell(0, 7, value)
        self.gap(2)

    def code(self, text):
        self.set_fill_color(244, 244, 245)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(24, 24, 27)
        self.multi_cell(0, 4.2, text, fill=True)
        self.gap(2)


def build(filename, kicker, footer, blocks):
    pdf = Packet(kicker, footer)
    pdf.add_page()
    for kind, *rest in blocks:
        if kind == "h1":
            pdf.h1(rest[0])
        elif kind == "lede":
            pdf.lede(rest[0])
        elif kind == "meta":
            pdf.meta(rest[0])
        elif kind == "h2":
            pdf.h2(rest[0])
        elif kind == "h3":
            pdf.h3(rest[0])
        elif kind == "p":
            pdf.p(rest[0])
        elif kind == "b":
            pdf.bullet(rest[0])
        elif kind == "code":
            pdf.code(rest[0])
        else:
            raise ValueError(kind)
    path = OUT / filename
    pdf.output(path)
    print(f"{filename}: {pdf.page} pages")


# ---------------------------------------------------------------------------
# Packet 1
# ---------------------------------------------------------------------------

build(
    "01-lock-accounts.pdf",
    "PHASE 1 OF 6   LOCK ACCOUNTS",
    "Phase 1  Lock accounts",
    [
        ("h1", "Phase 1. Lock accounts"),
        ("lede", "Security moves from 3.0 to 9.0. Do this phase before any other. The app currently lets a request invent a user, stores passwords as unsalted SHA-256, and can hand the password hash back in an export."),
        ("meta", [
            ("Score", "Security 3.0  ->  9.0"),
            ("Depends on", "Nothing. Start here."),
            ("Blocks", "Phases 2 through 6. Later tests assume these rules."),
            ("Touch", "database.py, server.py, app/core/config.py, requirements.txt, static/app.js, static/landing.html, extension/background.js, extension/manifest.json, extension/popup.js"),
            ("Leave alone", "Timer math, sheet problem lists, README wording, the split of app.js. Those are later phases."),
        ]),
        ("h2", "Outcome"),
        ("p", "After this phase a request is tied to one account only when it carries a session token issued by register or login. A missing or wrong token gets 401. A custom sheet, a progress row, and a backup belong to that account. Passwords survive an offline copy of the database. The browser launcher refuses non-web URLs and stops returning the local executable path."),
        ("h2", "What the code does today"),
        ("h3", "Passwords"),
        ("p", "database.hash_password is hashlib.sha256 with no salt. register_user and authenticate_user compare that digest directly. Minimum length is 6 characters in auth_register. get_current_user_id inserts new users with the password string default."),
        ("h3", "Identity"),
        ("p", "get_current_user_id in server.py accepts three things: a Bearer token, an X-User header that is 64 characters (treated as a token), or any other X-User string (treated as a username). If that username does not exist, the function INSERTs a user and returns the new id. Every progress, sheet, settings, and export route calls this function, so a header is enough to read or write that account."),
        ("h3", "CORS"),
        ("p", "server.py sets allow_origins to star and allow_credentials to True. app/core/config.py already lists the real origins in CORS_ORIGINS and nothing reads that list."),
        ("h3", "Sheets and export"),
        ("p", "get_custom_sheet_by_slug loads a sheet by slug alone. custom_sheets.slug is UNIQUE across every user, and save_custom_sheet uses ON CONFLICT(slug), so two people who pick the same title overwrite one sheet. export_backup runs SELECT * on users and puts the row in the JSON, which includes password_hash and session_token. The download header uses the name username, which is not defined in that function, so the endpoint raises NameError."),
        ("h3", "Browser launch and leaks"),
        ("p", "open_browser_endpoint passes payload.url to subprocess.Popen with no scheme check. It treats the process as cloud when RENDER is set, or PORT is set, or the OS is not Windows, so a Mac or Linux laptop never launches a browser, and any local PORT variable does the same. The JSON response includes browser_path. get_sheet_details also returns brave_path, which is a filesystem path."),
        ("h3", "Extension"),
        ("p", "extension/manifest.json grants https://*/*, every HTTPS site. extension/background.js on SOLVED_ACCEPTED POSTs to localhost with problem_id hard-coded to 1 and no token. After you require a token, that call will 401, and until you remove problem_id 1 it will also corrupt problem 1 for whoever is logged in."),
        ("h2", "Work, in this order"),
        ("h3", "1. Hash passwords so old rows still log in"),
        ("p", "Add a verify function in database.py. Keep hash_password as the writer of new hashes. Store scrypt from the Python standard library so you do not add a native package. Format the stored string as scrypt$<n>$<r>$<p>$<salt_hex>$<hash_hex> with a fresh 16-byte salt per password. Parameters: n=2**14, r=8, p=1."),
        ("bullet", "verify_password returns (ok, needs_rehash). If the stored value starts with scrypt$, check it with hmac.compare_digest. If it is 64 hex characters, compare it to SHA-256 and set needs_rehash when it matches."),
        ("bullet", "authenticate_user calls verify_password. On success with needs_rehash, UPDATE the row to the new scrypt string before you return the user."),
        ("bullet", "register_user writes only scrypt hashes."),
        ("bullet", "In auth_register, reject passwords shorter than 8 characters, and reject the exact password default."),
        ("bullet", "Do not log the password or the hash."),
        ("h3", "2. Issue a session and accept only that session"),
        ("p", "Keep the existing session_token column. register_user and authenticate_user already rotate it. Add logout_user(user_id) that sets session_token to NULL."),
        ("bullet", "Rewrite get_current_user_id so it reads only Authorization: Bearer <token>, calls get_user_by_token, and raises HTTPException 401 when the token is missing or unknown. Delete the X-User username branch and the INSERT that uses password default."),
        ("bullet", "Public routes, and only these: POST /api/auth/register, POST /api/auth/login, GET /healthz, GET /api/health, GET /api/badge/{username}.svg, GET /api/stats/platform, and the HTML pages."),
        ("bullet", "Add POST /api/auth/logout. It requires the bearer token, clears it, and returns status ok."),
        ("bullet", "In static/app.js, apiFetch already sends the bearer token from localStorage key anvil_token. After every response, if status is 401, remove anvil_token and set location to /login. Do the same in static/landing.html after a failed /api/auth/me."),
        ("bullet", "Confirm the landing page stores the token under the same key anvil_token. If it uses another key, change it to that one key."),
        ("h3", "3. Turn on the origin list you already wrote"),
        ("p", "In server.py, pass allow_origins=settings.CORS_ORIGINS and allow_credentials=True. Delete the star origin. Add http://localhost:8765 and http://127.0.0.1:8765 if they are not already in the list (they are). Add the Render origin and https://anvilbreaker.is-a.dev (they are)."),
        ("h3", "4. Make a custom sheet belong to one user"),
        ("bullet", "Change get_custom_sheet_by_slug to take user_id and add AND user_id = ? to the SELECT. get_sheet_details passes the current user. A miss raises 404."),
        ("bullet", "When creating a sheet, store the slug as {user_id}-{slugify(title)}. The column stays globally UNIQUE, and two accounts can both name a sheet Blind 75 without overwriting each other."),
        ("bullet", "delete_custom_sheet already filters on user_id. Keep that filter. Return 404 when rowcount is 0."),
        ("bullet", "list_sheets already loads custom sheets with get_custom_sheets(user_id). Leave that query as it is."),
        ("h3", "5. Fix the backup"),
        ("p", "In export_backup, stop selecting the raw user row into the JSON. Build the user object from username, email, daily_goal, streak, last_active_date, today_solved_count, active_sheet, preferred_browser, github_username, and leetcode_username. Omit password_hash, session_token, and brave_path. Progress, reviews, and custom_sheets stay, but strip problems_json only if you already expand it; raw problems_json is fine because it is that user's content."),
        ("p", "Set the download filename from user['username'] after replacing every character outside A-Za-z0-9._- with an underscore. The current f-string references username and crashes."),
        ("h3", "6. Constrain the browser launcher"),
        ("p", "Parse payload.url with urllib.parse.urlparse. Accept only schemes http and https. Reject a missing hostname, a url longer than 2000 characters, and a username or password embedded in the URL. On failure raise 400."),
        ("p", "Replace the cloud check. Today it is RENDER or PORT or os.name != nt. Change it to true only when RENDER, RAILWAY_ENVIRONMENT, or FLY_APP_NAME is set. On a cloud host, do not call Popen or webbrowser; return the url so the page can open it. On a laptop, launch as you do now."),
        ("p", "Remove browser_path from the JSON. In get_sheet_details, stop returning brave_path. Keep brave_available as a boolean."),
        ("h3", "7. Stop the extension from solving problem 1"),
        ("bullet", "In extension/manifest.json, delete the host permission https://*/*. Keep *://*.leetcode.com/* and http://localhost:8765/*. Add https://anvil-breaker.onrender.com/* and https://anvilbreaker.is-a.dev/*."),
        ("bullet", "In the popup, add a token field that saves to chrome.storage.local under anvil_token."),
        ("bullet", "In background.js, the SOLVED_ACCEPTED handler must read that token. If it is empty, do not POST. If it is present, send Authorization: Bearer. Do not send problem_id: 1. Skip the POST until phase 5 maps the LeetCode slug to a real problem id. A skipped sync is safe. A sync that marks problem 1 is not."),
        ("h2", "Check it yourself"),
        ("bullet", "Register with a new email. Confirm the password_hash column starts with scrypt$ and is not 64 hex characters."),
        ("bullet", "Log in. Call GET /api/auth/me with the bearer token and get the same user. Call it with no header and get 401."),
        ("bullet", "Call GET /api/sheets with header X-User: local_user and get 401. Confirm no new row appeared in users."),
        ("bullet", "Create a custom sheet as user A. As user B, GET /api/sheets/{that slug} and get 404."),
        ("bullet", "GET /api/export and confirm the JSON has no password_hash and no session_token, and the response is a file download rather than a 500."),
        ("bullet", "POST /api/open-browser with url file:///C:/Windows/win.ini and get 400. POST a normal https://leetcode.com URL on Windows and see the browser open, with no browser_path in the JSON."),
        ("bullet", "Log out. The same bearer token then gets 401."),
        ("h2", "Done when"),
        ("bullet", "No route creates a user as a side effect of a read or a progress write."),
        ("bullet", "New passwords are scrypt. An old SHA-256 password still logs in once and is rewritten."),
        ("bullet", "Export, custom sheets, and browser launch match the checks above."),
        ("bullet", "The extension no longer posts problem_id 1, and its manifest no longer allows every HTTPS origin."),
        ("p", "Phase 4 will turn these checks into pytest. In this phase, running them by hand is enough. Do not start the timer or review work until this list is true."),
    ],
)

# ---------------------------------------------------------------------------
# Packet 2
# ---------------------------------------------------------------------------

build(
    "02-make-the-protocol-true.pdf",
    "PHASE 2 OF 6   MAKE THE PROTOCOL TRUE",
    "Phase 2  Make the protocol true",
    [
        ("h1", "Phase 2. Make the protocol true"),
        ("lede", "Algorithms move from 4.0 to 9.0. The functions for spaced repetition and the adaptive timer already exist. They are called with constants, so a second solve never changes the interval, and a weak topic never changes the clock."),
        ("meta", [
            ("Score", "Algorithms 4.0  ->  9.0"),
            ("Depends on", "Phase 1. Status updates must belong to the logged-in user."),
            ("Blocks", "Phase 4 tests for interval growth, and phase 6's live study loop."),
            ("Touch", "database.py, server.py update_status and get_adaptive_protocol, app/core/protocol_engine.py only if a helper needs a home, static/app.js selectProblem and saveStatus, data migration path"),
            ("Leave alone", "The route-file split. Call the same URLs. Phase 3 moves them."),
        ]),
        ("h2", "Outcome"),
        ("p", "A help or failed mark schedules a review from the stored memory state, and the next mark on that problem continues from that state. The on-screen phases lengthen when the user fails that topic often. The streak counts calendar days. The JSON import runs once. Sheet cards show the number of problems actually loaded."),
        ("h2", "What the code does today"),
        ("h3", "Spaced repetition is reset on every call"),
        ("p", "calculate_sm2_interval in app/core/protocol_engine.py is a real SM-2 step: it updates the easiness factor, restarts the interval when quality is below 3, and uses 1 day, then 6 days, then previous interval times EF. update_status ignores the stored history and always calls it as calculate_sm2_interval(quality, repetitions=0, ef=2.5, prev_interval=1). StatusUpdateRequest has sm2_quality and the handler never reads it. Quality is hard-coded: clean=5, help=2, failed=1. There are no columns for repetitions, easiness factor, interval, or due date on user_progress. The reviews table stores a label string and a due date, and every help or failed mark INSERTs another row."),
        ("h3", "The adaptive timer ignores the user"),
        ("p", "GET /api/protocol/adaptive accepts difficulty and topic, then calls calculate_adaptive_budget(difficulty, user_fail_rate_topic=0.0). The fail-rate branch inside the function (add 1 minute to read and 2 minutes to pattern when the rate is above 0.4) never runs. static/app.js keeps its own HUD_PRESETS of 15, 25, and 45 minutes and never calls this endpoint. The 15-minute preset in the browser is 3 + 4 + 6 + 2, which is a different split from the README table of 3, 4, 6, 2 wait: README phase table is 0-3, 3-7, 7-13, 13-15, which is 3 + 4 + 6 + 2. That matches the 15m preset. The engine's Medium budget is 4 + 6 + 12 + 3 = 25. Nothing in the UI asks the engine which budget to use when a problem is selected."),
        ("h3", "Streak and daily count"),
        ("p", "When a problem newly becomes clean or help, update_status runs: UPDATE users SET today_solved_count = today_solved_count + 1, streak = max(streak, 1). The streak cannot grow. today_solved_count is never reset when the date changes. last_active_date is written at user creation and by the JSON migration, and not by this update."),
        ("h3", "Migration and counts"),
        ("p", "database.migrate_json_to_sqlite runs from server startup and from database.py __main__. It INSERT OR REPLACE progress and plain INSERT reviews, so every restart duplicates review rows for data/user_progress.json. list_sheets hard-codes problem_count 610, 95, 151, and 75 instead of len() on the loaded lists."),
        ("h2", "Work, in this order"),
        ("h3", "1. Store memory state on the progress row"),
        ("p", "In init_db, add columns to user_progress if they are missing, using the same ALTER TABLE try/except pattern already used for users:"),
        ("bullet", "sm2_repetitions INTEGER DEFAULT 0"),
        ("bullet", "sm2_ef REAL DEFAULT 2.5"),
        ("bullet", "sm2_interval INTEGER DEFAULT 0"),
        ("bullet", "sm2_due TEXT"),
        ("p", "Do not put this state only in the reviews table. Reviews are the queue the UI lists. The progress row is the memory the next calculation reads."),
        ("h3", "2. Continue SM-2 from the stored row"),
        ("p", "Inside update_status, before the upsert, SELECT sm2_repetitions, sm2_ef, sm2_interval for that user and problem. If there is no row, start from repetitions 0, ef 2.5, interval 0."),
        ("p", "Quality rule, applied on the server, not trusted from the client:"),
        ("bullet", "status clean and time_spent at or under the adaptive total for that difficulty: quality 5."),
        ("bullet", "status clean and over that budget: quality 4."),
        ("bullet", "status help: quality 2."),
        ("bullet", "status failed: quality 1."),
        ("bullet", "status unsolved: do not run SM-2 and do not insert a review. Clear nothing; leave the previous memory in place."),
        ("p", "Call calculate_sm2_interval with the stored repetitions, ef, and interval (use 1 as prev_interval when the stored interval is 0). Write the returned repetitions, easiness_factor, interval_days, and due_date onto the progress row in the same transaction as the status upsert."),
        ("p", "When status is help or failed, insert a review only if there is no incomplete review for that user, problem, and due_date. Add the check in SQL before the INSERT. Set review_type to a short stable label such as SM-2, and keep the due date in due_date. Stop embedding the interval only inside a display sentence, because the next calculation must not parse English."),
        ("p", "Return the sm2 object in the JSON as you do now, so the client can show the due date. In saveStatus, if result.sm2 exists, show the due_date in the existing notification for help and failed."),
        ("h3", "3. Roll the streak on the calendar"),
        ("p", "Add a function apply_activity(user_id, solved_new) and call it from update_status whenever status is clean or help."),
        ("bullet", "Read last_active_date, streak, and today_solved_count."),
        ("bullet", "If last_active_date is today: leave streak as it is. If this solve is a new clean or help (old status was not clean or help), add 1 to today_solved_count."),
        ("bullet", "If last_active_date is yesterday: set streak to streak + 1, set today_solved_count to 1 when this call is a new solve, otherwise 0, and set last_active_date to today."),
        ("bullet", "If last_active_date is older or empty: set streak to 1, set today_solved_count the same way, and set last_active_date to today."),
        ("p", "Delete the SQL that sets streak = max(streak, 1). A day with no solve does not increment the streak; the next solve after a gap resets it to 1. That is the rule to implement."),
        ("h3", "4. Feed a real fail rate into the budget"),
        ("p", "Add database.topic_fail_rate(user_id, topic) -> float. Topic matches user_progress.pattern when pattern is set, and otherwise you need the problem's chapter. Progress rows do not store chapter. For this phase, compute the rate from rows whose pattern equals the topic string the client sends. Rate = count(status=failed) / count(status in clean, help, failed). If the denominator is 0, return 0.0."),
        ("p", "Change GET /api/protocol/adaptive so it requires the bearer token from phase 1, reads difficulty and topic, loads the fail rate, and passes that float into calculate_adaptive_budget. Return the budget unchanged in shape: total_minutes and phases."),
        ("p", "In static/app.js selectProblem, after the problem is known, if the active preset is still the default 15m and the user has not pinned 25m, 45m, or custom during this session, GET /api/protocol/adaptive?difficulty=<level>&topic=<chapter_name> and call applyHudPreset('adaptive', data, true). Keep the 15, 25, 45, and custom buttons. If the user clicks one of those, set a flag state.presetPinned = true and do not overwrite it on the next problem. Choosing adaptive again clears the pin."),
        ("p", "Map difficulty with the problem's level field, which is already E, M, or H. URL-encode the topic."),
        ("p", "Expected budgets from the engine as it stands, with fail rate 0: Easy 2+3+7+3 = 15, Medium 4+6+12+3 = 25, Hard 7+10+22+6 = 45. With fail rate above 0.4, read gains 1 minute and pattern gains 2, and total_minutes grows by 3. The UI must display those phase ranges through buildPhaseConfig, which already accepts a phases array."),
        ("h3", "5. Run the JSON import once"),
        ("p", "At the end of a successful migrate_json_to_sqlite, write data/.migration_done next to the database. At the start of the function, return immediately if that file exists. Do this after the commit, so a failed migration retries next boot."),
        ("p", "Inside the review loop, skip an insert when a row already exists for that user_id, problem_id, and due_date. This protects databases that were duplicated before the flag existed. You do not have to delete old duplicate rows in this phase; add a one-time SQL note in the packet check: optional DELETE of exact duplicate reviews, keeping the lowest id."),
        ("h3", "6. Count problems from the data"),
        ("p", "In list_sheets, set problem_count from the length of the list each loader returns: load_json of problems.json for core-path, get_striver_sde_sheet, get_neetcode_150_sheet, and get_blind_75_sheet. Remove the literals 610, 95, 151, and 75. If loading a sheet twice is wasteful, count once and reuse, but correctness comes first. Titles can keep their names; the count on the card must match the array."),
        ("h2", "Worked example you should be able to reproduce"),
        ("p", "User fails topic Arrays twice, so fail rate is above 0.4. They open a Medium Arrays problem with the preset unpinned. The clock total is 28 minutes: read 5, pattern 8, code 12, cut 3. They mark the problem help. Memory starts at repetitions 0, so the due date is tomorrow and repetitions stays 0 because quality 2 is below 3. They later mark the same problem clean inside the budget: quality 5, repetitions becomes 1, interval 1 day. They mark it clean again: repetitions 2, interval 6 days. They mark it clean a third time: interval is round(6 * ef). ef started at 2.5 and has moved on each success. Write these three due dates down while you test. Phase 4 will assert the same sequence."),
        ("h2", "Check it yourself"),
        ("bullet", "Two help marks on one problem produce one incomplete review for the latest due date, not two identical rows, once the duplicate guard is in."),
        ("bullet", "A third clean mark returns interval_days greater than 6."),
        ("bullet", "Marking unsolved does not insert a review and does not zero the stored ef."),
        ("bullet", "Solve one problem yesterday (set last_active_date in SQLite to yesterday, streak 4) and solve another today. Streak becomes 5 and today_solved_count becomes 1."),
        ("bullet", "Set last_active_date to three days ago and solve. Streak becomes 1."),
        ("bullet", "With two failed and zero clean on pattern Arrays, the adaptive endpoint for difficulty M and topic Arrays returns total_minutes 28."),
        ("bullet", "Restart the server twice. The review count does not grow just because user_progress.json is still on disk."),
        ("bullet", "The sheet list counts equal the lengths of the four lists."),
        ("h2", "Done when"),
        ("bullet", "SM-2 fields survive in SQLite and the next update reads them."),
        ("bullet", "The timer on an unpinned session comes from /api/protocol/adaptive for that problem's level and chapter."),
        ("bullet", "Streak and today_solved_count follow the calendar rules above."),
        ("bullet", "Migration is one-shot, and sheet counts are computed."),
        ("p", "Leave calculate_sm2_interval's formula as it is. The bug is the call site, not the formula."),
    ],
)

print("packets 1-2 written, continuing is a separate process step")
