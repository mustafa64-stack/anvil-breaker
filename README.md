<div align="center">

<img src="static/hero_logo.jpg" alt="Anvil Breaker Logo" width="160" style="border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);" />

# ⚒️ ANVIL BREAKER™
### Break the Tutorial Anvil. 15 Minutes or Move On.

[![Live on anvilbreaker.is-a.dev](https://img.shields.io/badge/Domain-anvilbreaker.is--a.dev-F59E0B.svg?logo=googlechrome&logoColor=white)](https://anvilbreaker.is-a.dev)
[![Render Mirror](https://img.shields.io/badge/Render-Live%20Deploy-46E3B7.svg?logo=render&logoColor=white)](https://anvil-breaker.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-mustafa64--stack%2Fanvil--breaker-181717.svg?logo=github)](https://github.com/mustafa64-stack/anvil-breaker)
[![Author](https://img.shields.io/badge/Author-Mustafa%20Marjani-FFFFFF.svg?logo=github)](https://github.com/mustafa64-stack)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/Version-v2.4.1-amber.svg)](https://github.com/mustafa64-stack/anvil-breaker/releases)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-zinc.svg)](LICENSE)

**A high-performance algorithmic engineering system by Mustafa Marjani.**  
Enforces strict protocol timeboxing (15m, 25m, 45m, custom), browser native history routing, live DOM injection HUD inside LeetCode, multi-sheet curriculum, universal multi-browser engine, and private developer vaults.

[🚀 **Live Cloud App**](https://anvil-breaker.onrender.com) • [🌐 **Free Domain (anvilbreaker.is-a.dev)**](#-7-free-domain-anvilbreakeris-adev--deployment) • [📖 **Protocol Spec**](#-1-the-15-minute-protocol) • [🧩 **Browser Extension**](#-2-floating-mini-hud--chrome-extension)

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

## 🪟 2. Floating Mini HUD & Chrome/Brave Extension

Solve directly inside LeetCode without switching tabs:

* **Always-On-Top Mini HUD (Picture-in-Picture)**:
  Press <kbd>H</kbd> to launch a detached floating window that hovers over your editor via Chromium's Document Picture-in-Picture API. Real-time bi-directional sync via `BroadcastChannel`.
* **Native LeetCode DOM Injection**:
  The included Manifest V3 extension (`extension/`) injects a draggable floating HUD directly into `https://leetcode.com/problems/*`.
* **Automatic Submission Sniffer**:
  Listens for the LeetCode "Accepted" green toast and triggers background progress sync to your SQLite database and GitHub.

---

## 📚 3. Multi-Sheet Curriculum Engine

* **The Core Path (610 Problems)**: Complete 32-chapter algorithmic mastery sequence.
* **Striver's SDE Sheet (95 Problems)**: High-yield roadmap for FAANG/tier-1 software engineering rounds.
* **NeetCode 150 (151 Problems)**: Pattern-driven comprehensive interview syllabus.
* **Blind 75 (75 Problems)**: High-velocity sprint roadmap.
* **Self-Made Custom Sheets**: Curate personal sheets on the fly by pasting LeetCode URLs or titles.

---

## 🧠 4. The Defensible Engineering Moat

```
[ Problem Input ]
       │
       ▼
[ Adaptive Cognitive Protocol (ACP) ] ──► Dynamically adjusts budget based on Easy/Med/Hard
       │
       ▼
[ 5-Tier Failure Diagnostics ] ──► Pinpoints root cause failure:
       │                             1. Pattern Blindspot (missed pattern mapping)
       │                             2. Invariant Proof Failure (logic collapsed)
       │                             3. Boundary Bug (off-by-one, null edge cases)
       │                             4. Asymptotic Inefficiency / TLE (O(N^2) vs O(N log N))
       │                             5. Language Gotcha (overflow, custom comparator)
       ▼
[ SuperMemo-2 Spaced Repetition ] ──► Mathematically calculates optimal review review intervals
```

---

## 🚀 5. Getting Started Locally

```bash
# Clone the repository
git clone https://github.com/mustafa64-stack/anvil-breaker.git
cd anvil-breaker

# Install dependencies
pip install -r requirements.txt

# Run migrations and launch
python database.py
python -m uvicorn server:app --host 127.0.0.1 --port 8765 --reload
```
Open **`http://localhost:8765`** in Brave or Chrome.

---

## 🧩 6. Install the Browser Extension (Brave / Chrome)

1. Open your browser and navigate to `chrome://extensions` (or `brave://extensions`).
2. Enable **Developer mode** (toggle in top-right corner).
3. Click **Load unpacked** and select the `extension/` folder inside this repository.
4. Navigate to any problem on LeetCode—the Anvil Breaker floating HUD will attach automatically.

---

## 🌐 7. Free Domain (`anvilbreaker.is-a.dev`) & Deployment

### A. How to Claim `anvilbreaker.is-a.dev` (100% Free on GitHub)
`is-a.dev` is a free domain service run by the open-source community for developers. To activate `anvilbreaker.is-a.dev`:

1. Fork the official repository: **[`is-a-dev/register`](https://github.com/is-a-dev/register)**.
2. In the `domains/` folder, add a new file named **`anvilbreaker.json`** with the following content (pre-built in [`domains/anvilbreaker.json`](domains/anvilbreaker.json)):
   ```json
   {
     "description": "Anvil Breaker - High performance algorithmic engineering platform by Mustafa Marjani",
     "repo": "https://github.com/mustafa64-stack/anvil-breaker",
     "owner": {
       "username": "mustafa64-stack",
       "email": "mustafamarjani64@gmail.com"
     },
     "record": {
       "CNAME": "anvil-breaker.onrender.com"
     }
   }
   ```
3. Open a Pull Request on `is-a-dev/register`. The automated CI bot validates the record and merges it for free!
4. In your **Render Dashboard** -> **anvil-breaker** -> **Settings** -> **Custom Domains** -> Add **`anvilbreaker.is-a.dev`**.

### B. One-Click Cloud Deployment (Render Blueprint)
Deploy or replicate instantly to **Render.com** via [`render.yaml`](render.yaml):

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mustafa64-stack/anvil-breaker)

1. Click the button above or visit `https://render.com/deploy?repo=https://github.com/mustafa64-stack/anvil-breaker`.
2. Click **Create Blueprint**.
3. Live Cloud App: **`https://anvil-breaker.onrender.com`** (and `https://anvilbreaker.is-a.dev`).

---

## ⌨️ 8. Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| <kbd>Space</kbd> | Start / Pause Active Protocol Timer |
| <kbd>R</kbd> | Reset Protocol Timer |
| <kbd>H</kbd> | Pop-out Floating Mini HUD (Picture-in-Picture) |
| <kbd>B</kbd> | Open Current Problem in Brave Browser |
| <kbd>N</kbd> / <kbd>P</kbd> | Next / Previous Problem |
| <kbd>M</kbd> | Cycle Modes (15m ➔ 25m ➔ 45m) |
| <kbd>+</kbd> | Quick Extend +1 minute |
| <kbd>1</kbd> – <kbd>4</kbd> | Jump directly to Phase 1, 2, 3, or 4 |

---

## 📜 9. Proprietary License & Author

Copyright © 2026 **Mustafa Marjani** (`founder@anvilbreaker.dev`). All rights reserved.  
See [`LICENSE`](LICENSE) for complete proprietary source-available usage terms.
