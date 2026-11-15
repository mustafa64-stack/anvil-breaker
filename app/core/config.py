# app/core/config.py
import os

class Settings:
    PROJECT_NAME: str = "Anvil Breaker™"
    PROJECT_SUBTITLE: str = "Break the Tutorial Anvil. 15 Minutes or Move On."
    FOUNDER: str = "Mustafa Marjani"
    VERSION: str = "2.1.0-release"
    API_V1_STR: str = "/api"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    DB_PATH: str = os.path.join(DATA_DIR, "dsa_app.db")
    
    # Default Browser Executable Paths
    BRAVE_PATHS = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
    ]
    CHROME_PATHS = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    EDGE_PATHS = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]

    # Cognitive Failure Taxonomy (Defensible Moat)
    ERROR_TAXONOMY = {
        "idea": {
            "title": "Mental Model / Pattern Blindspot",
            "desc": "Failed to map to the correct algorithmic pattern (e.g. missed DP/monotonic stack)."
        },
        "proof": {
            "title": "Algorithmic Invariant Failure",
            "desc": "Algorithm sounded plausible but failed on correctness/edge invariants."
        },
        "boundary": {
            "title": "Boundary / Off-By-One Bug",
            "desc": "Logic was right, but tripped on pointer bounds, empty input, or indexing."
        },
        "speed": {
            "title": "Asymptotic Inefficiency / TLE",
            "desc": "Solution works but exceeds time/memory limit (e.g. O(N^2) instead of O(N log N))."
        },
        "gotcha": {
            "title": "Language / API Gotcha",
            "desc": "Language subtlety (e.g. 32-bit integer overflow, comparator inconsistency)."
        }
    }

settings = Settings()
