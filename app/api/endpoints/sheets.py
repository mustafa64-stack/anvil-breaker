# app/api/endpoints/sheets.py
import os
import json
import re
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import database
from app.core.config import settings
from app.core.dependencies import get_authenticated_user_id, get_optional_user_id
from app.core.security import sanitize_title
from app.sheets import sheets_loader

router = APIRouter(prefix="/sheets", tags=["sheets"])

class CustomSheetCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    problems: List[Dict[str, Any]]

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return default

@router.get("")
@router.get("/")
def list_sheets(user_id: int = Depends(get_optional_user_id)):
    """
    Returns available curriculum sheets with problem counts driven directly from loaded data.
    Custom sheets are scoped strictly to the calling user.
    """
    core_problems = load_json(os.path.join(settings.DATA_DIR, "problems.json"), [])
    striver_problems = sheets_loader.get_striver_sde_sheet()
    neetcode_problems = sheets_loader.get_neetcode_150_sheet()
    blind_problems = sheets_loader.get_blind_75_sheet()

    system_sheets = [
        {
            "slug": "core-path",
            "title": f"The Core Path ({len(core_problems)} Problems)",
            "author": "Core Path Companion",
            "problem_count": len(core_problems),
            "description": "32 chapters, one problem per technique in optimal order",
            "is_system": True
        },
        {
            "slug": "striver-sde",
            "title": "Striver's SDE Sheet",
            "author": "take U forward",
            "problem_count": len(striver_problems),
            "description": "The quintessential SDE interview preparation roadmap",
            "is_system": True
        },
        {
            "slug": "neetcode-150",
            "title": "NeetCode 150",
            "author": "NeetCode",
            "problem_count": len(neetcode_problems),
            "description": "Curated 150 problems covering all foundational patterns",
            "is_system": True
        },
        {
            "slug": "blind-75",
            "title": "Blind 75",
            "author": "Yangshun Tay",
            "problem_count": len(blind_problems),
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

@router.get("/{slug}")
def get_sheet_details(slug: str, user_id: int = Depends(get_optional_user_id)):
    """
    Retrieves full problem definitions for a given curriculum sheet.
    Custom sheets require ownership verification: unauthorized users receive 404.
    """
    problems = []
    chapters = []

    if slug == "core-path":
        problems = load_json(os.path.join(settings.DATA_DIR, "problems.json"), [])
        chapters = load_json(os.path.join(settings.DATA_DIR, "chapters.json"), [])
    elif slug == "striver-sde":
        problems = sheets_loader.get_striver_sde_sheet()
        topics = list(dict.fromkeys([p.get("chapter_name", "General") for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p.get("chapter_name") == t])} for i, t in enumerate(topics)]
    elif slug == "neetcode-150":
        problems = sheets_loader.get_neetcode_150_sheet()
        topics = list(dict.fromkeys([p.get("chapter_name", "General") for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p.get("chapter_name") == t])} for i, t in enumerate(topics)]
    elif slug == "blind-75":
        problems = sheets_loader.get_blind_75_sheet()
        topics = list(dict.fromkeys([p.get("chapter_name", "General") for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p.get("chapter_name") == t])} for i, t in enumerate(topics)]
    else:
        # Custom user sheet: strictly scoped to user_id
        custom = database.get_custom_sheet_by_slug(slug, user_id=user_id)
        if not custom:
            raise HTTPException(status_code=404, detail="Sheet not found or access denied")
        problems = custom.get("problems", [])
        topics = list(dict.fromkeys([p.get("chapter_name", "General") for p in problems]))
        topic_to_id = {t: i+1 for i, t in enumerate(topics)}
        for p in problems:
            p["chapter_id"] = topic_to_id.get(p.get("chapter_name", "General"), 1)
        chapters = [{"id": i+1, "name": t, "count": len([p for p in problems if p.get("chapter_name") == t])} for i, t in enumerate(topics)]

    return {
        "slug": slug,
        "problems": problems,
        "chapters": chapters,
        "count": len(problems)
    }

@router.post("/custom")
def create_custom_sheet(
    payload: CustomSheetCreateRequest,
    user_id: int = Depends(get_authenticated_user_id)
):
    """
    Creates a new custom curriculum roadmap scoped strictly to the authenticated user.
    """
    clean_title = sanitize_title(payload.title)
    if not clean_title:
        raise HTTPException(status_code=400, detail="Sheet title is required")
    
    slug_base = re.sub(r'[^a-z0-9]+', '-', clean_title.lower()).strip('-')
    if not slug_base:
        slug_base = "custom-sheet"
    slug = f"user-{user_id}-{slug_base}"

    for i, p in enumerate(payload.problems):
        if "id" not in p:
            p["id"] = 10000 + i + 1
        p["title"] = sanitize_title(p.get("title", f"Problem {i+1}"))
        p["chapter_name"] = sanitize_title(p.get("chapter_name", "General"))

    database.save_custom_sheet(
        user_id=user_id,
        slug=slug,
        title=clean_title,
        description=sanitize_title(payload.description or ""),
        problems=payload.problems
    )

    return {
        "status": "ok",
        "slug": slug,
        "title": clean_title,
        "problem_count": len(payload.problems)
    }

@router.delete("/custom/{slug}")
def delete_custom_sheet_endpoint(
    slug: str,
    user_id: int = Depends(get_authenticated_user_id)
):
    """
    Deletes a user's custom sheet after confirming ownership.
    """
    sheet = database.get_custom_sheet_by_slug(slug, user_id=user_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Custom sheet not found or unauthorized")
    
    database.delete_custom_sheet(user_id=user_id, slug=slug)
    return {"status": "ok", "deleted_slug": slug}

