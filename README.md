<div align="center">

<img src="static/hero_logo.jpg" alt="Anvil Breaker Logo" width="160" style="border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);" />

# ⚒️ ANVIL BREAKER™
### Break the Tutorial Anvil. 15 Minutes or Move On.

[![Live on anvilbreaker.is-a.dev](https://img.shields.io/badge/Domain-anvilbreaker.is--a.dev-F59E0B.svg?logo=googlechrome&logoColor=white)](https://anvilbreaker.is-a.dev)
[![Render Mirror](https://img.shields.io/badge/Render-Live%20Deploy-46E3B7.svg?logo=render&logoColor=white)](https://anvil-breaker.onrender.com)
[![Tests Passing](https://img.shields.io/badge/Tests-10%2F10%20Passed-emerald.svg?logo=pytest&logoColor=white)](tests/)
[![GitHub](https://img.shields.io/badge/GitHub-mustafa64--stack%2Fanvil--breaker-181717.svg?logo=github)](https://github.com/mustafa64-stack/anvil-breaker)
[![Author](https://img.shields.io/badge/Author-Mustafa%20Marjani-FFFFFF.svg?logo=github)](https://github.com/mustafa64-stack)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/Version-v2.5.0-amber.svg)](https://github.com/mustafa64-stack/anvil-breaker/releases)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-zinc.svg)](LICENSE)

**A high-performance algorithmic engineering system by Mustafa Marjani.**  
Enforces strict protocol timeboxing (15m, 25m, 45m, adaptive), browser native history routing, live DOM injection HUD inside LeetCode, multi-sheet curriculum, universal multi-browser engine, and private developer vaults.

[🚀 **Live Cloud App**](https://anvil-breaker.onrender.com) • [🌐 **Free Domain (anvilbreaker.is-a.dev)**](#-7-free-domain-anvilbreakeris-adev--deployment) • [📖 **Protocol Spec**](#-1-the-15-minute-protocol) • [🧠 **SM-2 & Adaptive Engine**](#-4-persisted-sm-2-decay--adaptive-cognitive-protocol) • [🧩 **Browser Extension**](#-2-floating-mini-hud--chrome-extension)

</div>

---

## ⚡ 1. The 15-Minute Protocol

Spending 90 minutes stuck on a single LeetCode problem is not learning—it is cognitive fatigue and disguised procrastination. **Anvil Breaker** stops tutorial hell by enforcing disciplined execution:

| Phase | Timebox | Objective & Cognitive Guardrails |
|---|---|---|
| **Phase 1: Read & Trace** | `00:00 – 03:00` | Read constraints & dry-run small inputs on pen & paper. Check duplicates, empty, negatives. |
| **Phase 2: Pick a Pattern** | `03:00 – 07:00` | Map problem to standard patterns (Two Pointers, Sliding Window, Monotonic Stack, BFS/DFS, DP). Formulate brute-force baseline. |
| **Phase 3: Code & Test** | `07:00 – 13:00` | Write clean production code without copy-pasting or leaning on AI chat completions. Dry-run sample edge cases before submitting. |
| **Phase 4: Cut Losses** | `13:00 – 15:00` | If still stuck at minute 13: **STOP**. Open editorial hints, understand the invariant proof, and type the working solution from scratch. |

---

## 🧠 4. Persisted SM-2 Decay & Adaptive Cognitive Protocol

```
[ Problem Input ]
       │
       ▼
[ Adaptive Cognitive Protocol (ACP) ] ──► Dynamically adjusts budget based on difficulty + topic fail rate
       │
       ▼
[ 5-Tier Failure Diagnostics ] ──► Pinpoints root cause failure:
       │                             1. Mental Model / Pattern Blindspot
       │                             2. Algorithmic Invariant Failure
       │                             3. Boundary / Off-By-One Bug
       │                             4. Asymptotic Inefficiency / TLE
       │                             5. Language / API Gotcha
       ▼
[ Persisted SuperMemo-2 Engine ] ──► Calculates retention decay curves stored in SQLite
```

### A. Persisted SuperMemo-2 (SM-2) Interval Growth
Retention parameters are persistently tracked per user per problem in `user_progress`:
* **Repetitions ($n$)**: Number of consecutive successful solves.
* **Easiness Factor ($EF$)**: Calibrated difficulty multiplier initialized at $2.5$ ($EF \ge 1.3$).
* **Interval Growth Schedule**:
  * Solve 1 (clean): Interval = **1 day**, Reps = **1**
  * Solve 2 (clean): Interval = **6 days**, Reps = **2**
  * Solve 3+ (clean): Interval = $\mathrm{round}(\mathrm{interval}_{prev} \times EF)$
* **Failure Stand-Down**: Quality $< 3$ resets repetitions to 0 and schedules a mandatory review for the next day.
* **Deduplication**: Automatically skips redundant review entries for the same problem and due date.

### B. Adaptive Cognitive Budget Engine
The protocol timer queries your historical performance on the problem's specific algorithmic topic:
$$\mathrm{Fail\ Rate}_{\mathrm{topic}} = \frac{\mathrm{Failed\ Attempts}_{\mathrm{topic}}}{\mathrm{Total\ Attempts}_{\mathrm{topic}}}$$
* When $\mathrm{Fail\ Rate}_{\mathrm{topic}} \le 0.4$: Standard budget is applied (Medium = 25 mins: 4m Read, 6m Pattern, 12m Code, 3m Cut).
* When $\mathrm{Fail\ Rate}_{\mathrm{topic}} > 0.4$: Cognitive friction detected. Phase 1 (Read) is allocated **+1 min** and Phase 2 (Pattern) is allocated **+2 mins** (Medium expands to 28 mins), giving you extra time to grasp invariants before writing code.

---

## 🔒 5. Security & Multi-Tenant Architecture

* **PBKDF2 Password Hashing**: Cryptographically slow HMAC-SHA256 with 100,000 iterations and 16-byte random salts.
* **Bearer Session Tokens**: Mutating routes require `Authorization: Bearer <session_token>`. Header impersonation (`X-User`) is strictly rejected.
* **Multi-Tenant Isolation**: Custom sheets and progress data are scoped to the authenticated `user_id`. Strangers cannot view or mutate another account's sheets.
* **Scrubbed Backups**: `/api/export` strips all `password_hash` and `session_token` fields from JSON exports.
* **Sanitized Browser Launcher**: `/api/open-browser` validates protocol schemes, permitting only `http://` and `https://`.
* **Tighter Extension Permissions**: Chrome/Brave extension host permissions are scoped exclusively to `leetcode.com` and `cses.fi`.

---

## 📚 3. Multi-Sheet Curriculum Engine

Problem counts are driven dynamically from loaded curriculum collections:
* **The Core Path (610 Problems)**: Complete 32-chapter algorithmic mastery sequence.
* **Striver's SDE Sheet (95 Problems)**: High-yield roadmap for FAANG/tier-1 software engineering rounds.
* **NeetCode 150 (151 Problems)**: Pattern-driven comprehensive interview syllabus.
* **Blind 75 (75 Problems)**: High-velocity sprint roadmap.
* **Self-Made Custom Sheets**: Curate personal sheets on the fly with multi-tenant privacy.

---

## 🪟 2. Floating Mini HUD & Chrome/Brave Extension

Solve directly inside LeetCode without switching tabs:
* **Always-On-Top Mini HUD (Picture-in-Picture)**:
  Press <kbd>H</kbd> to launch a detached floating window that hovers over your editor via Chromium's Document Picture-in-Picture API. Real-time bi-directional sync via `BroadcastChannel`.
* **Native LeetCode DOM Injection**:
  The included Manifest V3 extension (`extension/`) injects a draggable floating HUD directly into `https://leetcode.com/problems/*`.
* **Automatic Submission Sniffer**:
  Listens for the LeetCode "Accepted" green toast and triggers background progress sync to your SQLite database.

---

## 🚀 6. Getting Started Locally & Running Tests

```bash
# Clone the repository
git clone https://github.com/mustafa64-stack/anvil-breaker.git
cd anvil-breaker

# Install dependencies
pip install -r requirements.txt

# Run pytest validation suite (10/10 tests pass)
python -m pytest tests/

# Launch development server
python server.py
```
Open **`http://localhost:8765`** in Brave, Chrome, Edge, or Firefox.

---

## 🌐 7. Free Domain (`anvilbreaker.is-a.dev`) & Deployment

### A. Free Domain Registration (`anvilbreaker.is-a.dev`)
`is-a.dev` provides 100% free developer subdomains:
* Pre-configured record: [`domains/anvilbreaker.json`](domains/anvilbreaker.json)
* PR #61445 submitted to `is-a-dev/register` pointing `anvilbreaker.is-a.dev` CNAME directly to `anvil-breaker.onrender.com`.

### B. One-Click Cloud Deployment (Render Blueprint)
Deploy or replicate instantly to **Render.com** via [`render.yaml`](render.yaml):

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mustafa64-stack/anvil-breaker)

Live Cloud App: **`https://anvil-breaker.onrender.com`** (and `https://anvilbreaker.is-a.dev`).

---

## ⌨️ 8. Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| <kbd>Space</kbd> | Start / Pause Active Protocol Timer |
| <kbd>R</kbd> | Reset Protocol Timer |
| <kbd>H</kbd> | Pop-out Floating Mini HUD (Picture-in-Picture) |
| <kbd>B</kbd> | Open Current Problem in Platform Browser |
| <kbd>Alt</kbd> + <kbd>C</kbd> | Switch to Curriculum Roadmap View |
| <kbd>Alt</kbd> + <kbd>S</kbd> | Switch to 15m Protocol Solver View |

---

<div align="center">
  <sub>Architected with obsessive focus by <strong>Mustafa Marjani</strong> • Anvil Breaker™ v2.5.0</sub>
</div>
