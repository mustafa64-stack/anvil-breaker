# DSA Core Path & Adaptive Protocol Command Center

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](Dockerfile)
[![PWA Ready](https://img.shields.io/badge/PWA-Installable-purple.svg)](static/manifest.json)
[![DSA 15-Min Protocol](http://localhost:8765/api/badge/local_user.svg)](http://localhost:8765)

A professional, high-performance DSA companion application built for engineering mastery. Features a dynamic timebox HUD enforcing a strict **4-stage cognitive protocol**, a **floating Always-On-Top Mini HUD / Picture-in-Picture (PiP)** timer, multi-sheet architecture (**Core Path 610, Striver's SDE Sheet, NeetCode 150, Blind 75, and Self-Made Sheets**), native **Brave Browser** automation with **LeetHub/LeetSync GitHub push**, an **SM-2 algorithmic memory decay engine**, and a live **dynamic SVG GitHub badge generator**.

---

## ⚡ 1. The Dynamic Cognitive Protocol HUD

Unlike static timers, the app provides real-time ambient HUD controls with dynamic phase re-allocation:

| Mode | Total Time | Phase 1: Read & Trace | Phase 2: Pick a Pattern | Phase 3: Code & Test | Phase 4: Cut Losses |
|---|---|---|---|---|---|
| **15m Speedrun** | **15 min** | 03:00 (Sketch edge cases) | 04:00 (Map algorithm) | 06:00 (Clean code) | 02:00 (Editorial & memory re-solve) |
| **25m Standard** | **25 min** | 05:00 (Dry-run constraints) | 05:00 (Brute force & invariant) | 11:00 (Dry-run test cases) | 04:00 (Deep breakdown & re-solve) |
| **45m FAANG Mock** | **45 min** | 08:00 (Interview clarify) | 08:00 (Tradeoff discussion) | 22:00 (Production code) | 07:00 (Complexity & edge proofs) |
| **Custom HUD** | **Variable** | Customizable via modal | Customizable via modal | Customizable via modal | Customizable via modal |

### Additional HUD Controls:
- **`+1m` / `+5m` Quick Extend**: Instantly adds time without resetting phase state.
- **Compact Focus Mode**: Toggles stepper visibility for an ultra-clean distraction-free HUD.
- **Audio Chimes**: Web Audio API synthesized frequencies signal phase changes and countdown limits.

---

## 🪟 2. Floating Pop-Out Mini HUD & Picture-in-Picture (PiP)

When coding inside LeetCode in Brave or typing in your IDE, you don't need to switch back to the command center to watch the clock:

1. **Pop-out Mini Window (Always-On-Top PiP)**:
   - Click **"Pop-out HUD"** (or hit <kbd>H</kbd>).
   - Utilizes the native Chromium **Document Picture-in-Picture API** or a detached popup (`/mini-hud`) that floats over your LeetCode code editor.
   - Synchronized bi-directionally in real-time via `BroadcastChannel`: pausing, resetting, or jumping phases in the mini popup instantly reflects in the main application, and vice versa!
2. **In-Page Docked Mini Corner Timer**:
   - When reading through long constraints, problem hints, or writing notes in the scratchpad, a compact floating HUD remains pinned in the bottom-right corner with live time, phase indicator, and 1-click play/pause.

---

## 📚 3. Multi-Sheet Engine & Self-Made Sheets

Switch between top curated roadmaps or curate your own with 1-click:

1. **The Core Path (610 Problems across 32 Chapters)**:
   - Full sequential curriculum from foundations to advanced dynamic programming, trees, graphs, string automations, and game theory.
2. **Striver's SDE Sheet (95 Problems across 19 Topics)**:
   - The quintessential roadmap for software development engineer interviews.
3. **NeetCode 150 (151 Problems across 18 Topics)**:
   - Comprehensive pattern coverage across all LeetCode data structure categories.
4. **Blind 75 (75 Problems across 13 Topics)**:
   - High-yield sprint roadmap for rapid interview preparation.
5. **Self-Made Sheets (Custom User Curations)**:
   - Click **➕ Create Self-Made Sheet**.
   - Paste any combination of LeetCode URLs (`https://leetcode.com/problems/trapping-rain-water/`) or problem titles (`Word Search II`).
   - The system automatically parses slugs, titles, URLs, and organizes them into your customized track.

---

## 🛡️ 4. The Defensible Product Moat ("Fan With Wings")

Rather than a generic timer that can easily be copied, this platform introduces an algorithmic moat:

```
[ Problem Input ]
       │
       ▼
[ Adaptive Cognitive Protocol (ACP) ] ──► Dynamically scales timebox by difficulty (E/M/H) & cognitive load
       │
       ▼
[ 5-Tier Cognitive Failure Diagnostics ] ──► Classifies root cause failure:
       │                                     1. Pattern Blindspot (missed trick)
       │                                     2. Invariant Proof (flawed edge proofs)
       │                                     3. Boundary Bug (off-by-one, nulls)
       │                                     4. TLE / Asymptotic (complexity)
       │                                     5. Language Gotcha (overflow, comparator)
       ▼
[ SM-2 Algorithmic Spaced Repetition ] ──► Calculates optimal memory decay curve (EF & Interval Days)
```

- **ACP (Adaptive Cognitive Protocol)**: Dynamically scales phase budgets based on problem level and cognitive load.
- **SM-2 Memory Decay Algorithm**: Calculates optimal review intervals based on SuperMemo-2 mathematical models ($EF' = EF + (0.1 - (5 - q) \times (0.08 + (5 - q) \times 0.02))$).
- **Cognitive Failure Taxonomy**: Replaces vague notes with actionable algorithmic diagnostics.

---

## 🦁 5. Brave Browser & GitHub Auto-Sync

### How it works:
1. When you click **"Open in Brave"** (or hit <kbd>B</kbd>), the app triggers `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe` directly to the active problem on LeetCode.
2. Ensure you have **LeetHub v2** or **LeetSync** installed in Brave and authorized with your GitHub repository (e.g. `dsa-solutions`).
3. Whenever LeetCode shows **Accepted**, the extension pushes the clean code, runtime metrics, and problem README to GitHub automatically.

---

## 📈 6. Live GitHub Profile Badge Generator

Embed a live updating badge directly in your GitHub profile `README.md`:

```markdown
[![DSA 15-Min Protocol](http://localhost:8765/api/badge/local_user.svg)](http://localhost:8765)
```

The endpoint `/api/badge/{username}.svg` dynamically renders an SVG displaying your current streak and verified problem solves.

---

## 🔒 7. Security & Software Engineering Standards

- **OWASP Defense-in-Depth**: Strict security headers middleware (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Strict-Transport-Security`, `Content-Security-Policy`).
- **Input Sanitization**: URL and title sanitizers prevent XSS injection attacks.
- **SQLite WAL Mode**: Thread-safe ACID persistence with automatic migrations from JSON.
- **Progressive Web App (PWA)**: Includes `manifest.json` for installation as a standalone desktop app.

---

## 🌐 8. Real Cloud Deployment (Out of Localhost)

To deploy your companion app to the cloud so you and others can access it anywhere from any phone or computer:

### Option A: Free Cloud Deployment via Render.com (Recommended)
1. Push this directory to your GitHub account (e.g., `github.com/<your-username>/dsa-protocol-hub`).
2. Log into [Render.com](https://render.com) and click **New + ➔ Blueprint**.
3. Select your repository. Render automatically reads `render.yaml`, spins up the Python 3.12 environment, initializes the SQLite database with persistent disk storage, provisions free SSL/TLS HTTPS certificates, and deploys it live at `https://dsa-protocol-hub.onrender.com`!

### Option B: 1-Click Deploy via Railway.app
1. Install Railway CLI: `npm i -g @railway/cli` (or connect your GitHub repo on [railway.app](https://railway.app)).
2. Run in this directory:
   ```bash
   railway up
   ```
   Railway automatically detects `railway.json` and `Dockerfile`, handles the `$PORT` variable, and provides a live `up.railway.app` public domain.

### Option C: Global Edge Deployment via Fly.io
1. Install Flyctl and authenticate: `fly auth login`.
2. Run:
   ```bash
   fly launch --config fly.toml
   fly deploy
   ```
   Fly.io sets up zero-downtime global edge routing with persistent volume mounting for SQLite.

### Option D: Docker Container Deployment
```bash
docker-compose up -d --build
```
Access at `http://localhost:8765` or your server's public IP.

---

## ⌨️ 9. Keyboard Shortcuts

| Key | Action |
|---|---|
| <kbd>Space</kbd> | Start / Pause Active Timer |
| <kbd>R</kbd> | Reset Protocol Timer |
| <kbd>H</kbd> | Pop-out Floating Mini HUD (Picture-in-Picture) |
| <kbd>B</kbd> | Open Problem directly in Brave Browser |
| <kbd>N</kbd> | Advance to Next Problem in sequence |
| <kbd>P</kbd> | Move to Previous Problem |
| <kbd>M</kbd> | Cycle HUD Modes (15m ➔ 25m ➔ 45m) |
| <kbd>+</kbd> | Quick Extend +1 minute |
| <kbd>1</kbd> - <kbd>4</kbd> | Jump directly to Phase 1, 2, 3, or 4 |
