# app/api/endpoints/browser.py
import os
import subprocess
import webbrowser
from typing import Optional
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.core.security import sanitize_url
from app.sheets import sheets_loader

router = APIRouter(tags=["browser"])

class OpenBrowserRequest(BaseModel):
    problem_id: Optional[int] = None
    sheet_slug: Optional[str] = "core-path"
    url: Optional[str] = None
    browser: Optional[str] = "auto"

def detect_browser_path(browser: str = "auto") -> Optional[str]:
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

def validate_http_url(url: str) -> str:
    """
    Enforces strict protocol security: only http and https are allowed.
    Rejects file://, javascript:, data:, and shell injection vectors.
    """
    clean = sanitize_url(url)
    parsed = urlparse(clean)
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=400, 
            detail=f"Security rejection: Invalid URL scheme '{parsed.scheme}'. Only http and https protocols are allowed."
        )
    return clean

@router.post("/open-browser")
def open_browser_endpoint(payload: OpenBrowserRequest):
    url = None
    if payload.url:
        url = payload.url
    elif payload.problem_id is not None:
        sheet = payload.sheet_slug or "core-path"
        if sheet == "striver-sde":
            striver_probs = sheets_loader.get_striver_sde_sheet()
            prob = next((p for p in striver_probs if p["id"] == payload.problem_id), None)
            if prob and prob.get("url"):
                url = prob["url"]
        elif sheet == "neetcode-150":
            neet_probs = sheets_loader.get_neetcode_150_sheet()
            prob = next((p for p in neet_probs if p["id"] == payload.problem_id), None)
            if prob and prob.get("url"):
                url = prob["url"]
        elif sheet == "blind-75":
            blind_probs = sheets_loader.get_blind_75_sheet()
            prob = next((p for p in blind_probs if p["id"] == payload.problem_id), None)
            if prob and prob.get("url"):
                url = prob["url"]

    if not url:
        url = f"https://leetcode.com/problemset/all/?page={payload.problem_id or 1}"

    # Strict Protocol Validation (Phase 1 Security Gate)
    clean_url = validate_http_url(url)

    is_cloud = os.environ.get("RENDER") is not None or os.environ.get("PORT") is not None
    chosen_browser = (payload.browser or "auto").lower().strip()
    browser_exe = detect_browser_path(chosen_browser)

    launched_direct = False
    if not is_cloud and browser_exe and os.path.exists(browser_exe):
        try:
            subprocess.Popen([browser_exe, clean_url])
            launched_direct = True
        except Exception as e:
            print(f"Failed to spawn {browser_exe}: {e}")

    if not is_cloud and not launched_direct:
        try:
            webbrowser.open_new_tab(clean_url)
            launched_direct = True
        except Exception as e:
            print(f"Failed to open via webbrowser: {e}")

    return {
        "status": "ok",
        "url": clean_url,
        "browser": chosen_browser,
        "is_cloud": is_cloud,
        "launched_direct": launched_direct,
        "browser_path": browser_exe
    }

@router.post("/open-brave")
def open_brave_legacy(payload: OpenBrowserRequest):
    """Backward compatibility endpoint for older clients"""
    payload.browser = "brave"
    return open_browser_endpoint(payload)

