# app/core/protocol_engine.py
"""
Adaptive Cognitive Protocol Engine (ACPE) & Memory Decay (SM-2 variant).
Proprietary algorithmic core providing a defensible moat against shallow clones.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta

def calculate_adaptive_budget(difficulty: str, user_fail_rate_topic: float = 0.0) -> Dict[str, Any]:
    """
    Dynamically computes phase minute allocations based on problem difficulty
    and user cognitive friction score.
    """
    diff = (difficulty or "M").upper()
    
    if diff == "E":
        base_read = 2
        base_pattern = 3
        base_code = 7
        base_cut = 3
    elif diff == "H":
        base_read = 7
        base_pattern = 10
        base_code = 22
        base_cut = 6
    else: # Medium
        base_read = 4
        base_pattern = 6
        base_code = 12
        base_cut = 3

    # Dynamic adjustment based on cognitive friction on this topic
    if user_fail_rate_topic > 0.4:
        base_read += 1
        base_pattern += 2

    total_mins = base_read + base_pattern + base_code + base_cut
    
    return {
        "total_minutes": total_mins,
        "phases": [
            {"id": 1, "name": "Read & Trace", "minutes": base_read},
            {"id": 2, "name": "Pick a Pattern", "minutes": base_pattern},
            {"id": 3, "name": "Code & Test", "minutes": base_code},
            {"id": 4, "name": "Cut Your Losses", "minutes": base_cut}
        ]
    }

def calculate_sm2_interval(quality: int, repetitions: int, ef: float, prev_interval: int) -> Dict[str, Any]:
    """
    SuperMemo-2 (SM-2) memory retention engine calibrated for algorithmic patterns.
    quality:
      5: Perfect clean solve in Phase 1-3 without peeking
      4: Clean solve with minor delay
      3: Needed 1 editorial hint
      2: Solved only after reading editorial (Rule 3)
      1: Stood down / failed (Rule 4)
    """
    quality = max(0, min(5, quality))
    
    # Calculate new Easiness Factor (EF)
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3

    if quality < 3:
        # Failure / needed heavy editorial -> restart repetition sequence
        new_repetitions = 0
        new_interval = 1 # Re-attempt next day
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = int(round(prev_interval * new_ef))

    due_date = (datetime.now() + timedelta(days=new_interval)).strftime("%Y-%m-%d")
    
    return {
        "repetitions": new_repetitions,
        "easiness_factor": round(new_ef, 2),
        "interval_days": new_interval,
        "due_date": due_date
    }

