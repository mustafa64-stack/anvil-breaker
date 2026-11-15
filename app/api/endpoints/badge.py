# app/api/endpoints/badge.py
from fastapi import APIRouter, Response
import database

router = APIRouter()

@router.get("/badge/{username}.svg")
def generate_user_badge(username: str):
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    streak = 1
    today_count = 0
    total_solved = 0
    
    if user:
        streak = user["streak"] or 1
        today_count = user["today_solved_count"] or 0
        c.execute("SELECT COUNT(*) as cnt FROM user_progress WHERE user_id = ? AND status IN ('clean', 'help')", (user["id"],))
        row = c.fetchone()
        if row:
            total_solved = row["cnt"]
    conn.close()

    # Generate crisp SVG badge (Shields.io style with cyber-glow)
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="330" height="34" viewBox="0 0 330 34" role="img" aria-label="Anvil Breaker 15-Min Protocol">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="50%" stop-color="#ef4444"/>
      <stop offset="100%" stop-color="#6366f1"/>
    </linearGradient>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0b0f19"/>
    </linearGradient>
  </defs>
  <rect width="330" height="34" rx="8" fill="url(#bg)" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
  
  <!-- Left Shield Badge -->
  <rect x="3" y="3" width="148" height="28" rx="6" fill="url(#grad)"/>
  <text x="10" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="900" fill="#ffffff" letter-spacing="0.5">⚒️ ANVIL BREAKER</text>
  
  <!-- Right Stats Section -->
  <text x="160" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#94a3b8">
    🔥 <tspan fill="#f59e0b" font-weight="700">{streak}d streak</tspan> · <tspan fill="#10b981" font-weight="700">{total_solved} solved</tspan>
  </text>
</svg>"""

    return Response(content=svg_content, media_type="image/svg+xml", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })

