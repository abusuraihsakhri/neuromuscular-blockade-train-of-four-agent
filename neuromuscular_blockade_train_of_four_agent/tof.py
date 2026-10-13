"""Deterministic, educational interpretation of neuromuscular blockade monitoring.

This module reports monitoring categories from the 2023 ASA practice guideline.
It does not select reversal drugs, calculate doses, or determine extubation readiness.
"""
import math
from typing import Optional


def interpret_tof(count: int, ptc: Optional[int] = None, ratio: Optional[float] = None) -> dict:
    """Classify an observed TOF count (0–4), PTC, and quantitative TOF ratio.

    PTC is relevant only when no TOF twitch is observed. A TOF ratio requires
    four detectable twitches. Missing measurements remain indeterminate.
    """
    if type(count) is not int or not 0 <= count <= 4:
        raise ValueError("TOF count must be an integer from 0 to 4.")
    if ptc is not None:
        if type(ptc) is not int or not 0 <= ptc <= 30:
            raise ValueError("PTC must be an integer from 0 to 30.")
        if count != 0:
            raise ValueError("PTC is only interpreted when TOF count is zero.")
    if ratio is not None:
        if isinstance(ratio, bool) or not isinstance(ratio, (int, float)):
            raise ValueError("TOF ratio must be a finite number.")
        if not math.isfinite(ratio) or not 0 <= ratio <= 1.5:
            raise ValueError("TOF ratio must be a finite number from 0 to 1.5.")
        if count != 4:
            raise ValueError("A TOF ratio is only interpreted with four detected twitches.")

    if count == 0:
        if ptc is None:
            category = "INDETERMINATE"
            detail = "No TOF response; PTC was not supplied, so deep versus complete block cannot be distinguished."
        elif ptc == 0:
            category = "COMPLETE"
            detail = "No TOF response or post-tetanic response was observed."
        else:
            category = "DEEP"
            detail = "No TOF response; one or more post-tetanic responses were observed."
    elif count <= 3:
        category = "MODERATE"
        detail = f"{count} of 4 TOF twitches detected."
    elif ratio is None:
        category = "INDETERMINATE"
        detail = "All four twitches detected; a quantitative TOF ratio is required to assess recovery."
    elif ratio < 0.4:
        category = "SHALLOW"
        detail = "Four twitches with a quantitative TOF ratio below 0.4."
    elif ratio < 0.9:
        category = "MINIMAL"
        detail = "Four twitches with a quantitative TOF ratio from 0.4 to below 0.9."
    else:
        category = "RECOVERED"
        detail = "Quantitative TOF ratio is at least 0.9."

    return {
        "category": category,
        "detail": detail,
        "recovery_threshold_met": category == "RECOVERED",
        "note": (
            "Educational classification only. Clinical decisions require validated "
            "quantitative monitoring at the adductor pollicis, clinical assessment, "
            "and applicable professional guidance."
        ),
        "source": "2023 ASA practice guidelines, DOI:10.1097/ALN.0000000000004379",
    }
