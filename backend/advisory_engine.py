"""
advisory_engine.py — Rule-Based Irrigation Advisory Engine
═══════════════════════════════════════════════════════════
Smart Irrigation Advisory System · Hackathon Backend

Uses Pandas DataFrames to evaluate soil moisture, crop-stage water
requirements, and weather forecast data to produce actionable irrigation
recommendations.

Decision Logic:
  1. Moisture ≥ threshold           → WAIT (soil is adequately moist)
  2. Rain ≥ 60 % AND covers ≥ 70 % → WAIT (rain will satisfy the crop)
  3. Rain partial coverage          → IRRIGATE (deficit minus expected rain)
  4. Otherwise                      → IRRIGATE (full deficit)

The `deficit_factor` scales the recommendation proportionally to how far
below the threshold current moisture sits, matching the original Cloud
Functions logic exactly.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


# ── Crop-stage water requirement reference table ─────────────────────
# Pre-loaded as a Pandas DataFrame for rapid lookup during advisory runs.
CROP_RULES_DF = pd.DataFrame([
    # Rice
    {"crop_type": "Rice", "growth_stage": "Germination",  "water_requirement_mm_per_day": 8.0,  "moisture_threshold_percent": 65.0},
    {"crop_type": "Rice", "growth_stage": "Vegetative",   "water_requirement_mm_per_day": 10.0, "moisture_threshold_percent": 55.0},
    {"crop_type": "Rice", "growth_stage": "Flowering",    "water_requirement_mm_per_day": 12.0, "moisture_threshold_percent": 60.0},
    {"crop_type": "Rice", "growth_stage": "Maturity",     "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 45.0},
    # Maize
    {"crop_type": "Maize", "growth_stage": "Germination", "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 55.0},
    {"crop_type": "Maize", "growth_stage": "Vegetative",  "water_requirement_mm_per_day": 8.0,  "moisture_threshold_percent": 50.0},
    {"crop_type": "Maize", "growth_stage": "Flowering",   "water_requirement_mm_per_day": 10.0, "moisture_threshold_percent": 55.0},
    {"crop_type": "Maize", "growth_stage": "Maturity",    "water_requirement_mm_per_day": 5.0,  "moisture_threshold_percent": 40.0},
    # Chili
    {"crop_type": "Chili", "growth_stage": "Germination", "water_requirement_mm_per_day": 5.0,  "moisture_threshold_percent": 60.0},
    {"crop_type": "Chili", "growth_stage": "Vegetative",  "water_requirement_mm_per_day": 7.0,  "moisture_threshold_percent": 50.0},
    {"crop_type": "Chili", "growth_stage": "Flowering",   "water_requirement_mm_per_day": 9.0,  "moisture_threshold_percent": 55.0},
    {"crop_type": "Chili", "growth_stage": "Maturity",    "water_requirement_mm_per_day": 4.0,  "moisture_threshold_percent": 40.0},
    # Cotton
    {"crop_type": "Cotton", "growth_stage": "Germination", "water_requirement_mm_per_day": 5.5, "moisture_threshold_percent": 55.0},
    {"crop_type": "Cotton", "growth_stage": "Vegetative",  "water_requirement_mm_per_day": 7.5, "moisture_threshold_percent": 48.0},
    {"crop_type": "Cotton", "growth_stage": "Flowering",   "water_requirement_mm_per_day": 9.5, "moisture_threshold_percent": 52.0},
    {"crop_type": "Cotton", "growth_stage": "Maturity",    "water_requirement_mm_per_day": 4.5, "moisture_threshold_percent": 38.0},
    # Sugarcane
    {"crop_type": "Sugarcane", "growth_stage": "Germination", "water_requirement_mm_per_day": 7.0,  "moisture_threshold_percent": 60.0},
    {"crop_type": "Sugarcane", "growth_stage": "Vegetative",  "water_requirement_mm_per_day": 10.0, "moisture_threshold_percent": 55.0},
    {"crop_type": "Sugarcane", "growth_stage": "Flowering",   "water_requirement_mm_per_day": 11.0, "moisture_threshold_percent": 58.0},
    {"crop_type": "Sugarcane", "growth_stage": "Maturity",    "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 42.0},
])


def lookup_crop_rule(crop_type: str, growth_stage: str) -> Optional[Dict[str, Any]]:
    """
    Look up water-requirement rule for a given crop + stage from the
    reference DataFrame.  Returns None if no match is found.
    """
    mask = (
        (CROP_RULES_DF["crop_type"].str.lower() == crop_type.strip().lower())
        & (CROP_RULES_DF["growth_stage"].str.lower() == growth_stage.strip().lower())
    )
    match = CROP_RULES_DF.loc[mask]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_recommendation(
    moisture_percent: float,
    crop_stage_rule: Dict[str, Any],
    rain_probability_percent: float,
    expected_rainfall_mm: float,
    field_area_acres: float = 1.0,
) -> Dict[str, Any]:
    """
    Generate an irrigation recommendation.

    Parameters
    ----------
    moisture_percent : float
        Latest soil moisture reading (0 – 100).
    crop_stage_rule : dict
        Must contain 'moisture_threshold_percent' and 'water_requirement_mm_per_day'.
    rain_probability_percent : float
        Forecast rain probability (0 – 100).
    expected_rainfall_mm : float
        Expected rainfall amount in mm.
    field_area_acres : float
        Field size (used to calculate total litres).

    Returns
    -------
    dict with keys: recommendation, amount_mm, total_litres, reason,
                    moisture_percent, threshold_percent, deficit_factor,
                    rain_adjustment_mm, confidence_score
    """
    threshold = float(crop_stage_rule.get("moisture_threshold_percent", 50.0))
    daily_need = float(crop_stage_rule.get("water_requirement_mm_per_day", 10.0))

    # Build a single-row evaluation DataFrame (demonstrates Pandas usage)
    eval_df = pd.DataFrame([{
        "moisture":    moisture_percent,
        "threshold":   threshold,
        "daily_need":  daily_need,
        "rain_prob":   rain_probability_percent,
        "exp_rain":    expected_rainfall_mm,
        "area_acres":  field_area_acres,
    }])

    # Derived columns
    eval_df["is_moist_enough"]    = eval_df["moisture"] >= eval_df["threshold"]
    eval_df["deficit_factor"]     = np.clip((eval_df["threshold"] - eval_df["moisture"]) / eval_df["threshold"], 0, 1)
    eval_df["rain_covers_need"]   = (eval_df["rain_prob"] >= 60) & (eval_df["exp_rain"] >= 0.7 * eval_df["daily_need"])
    eval_df["rain_adjustment"]    = np.where(eval_df["rain_prob"] >= 40, eval_df["exp_rain"] * (eval_df["rain_prob"] / 100), 0)
    eval_df["raw_recommendation"] = np.round(eval_df["daily_need"] * (1 + eval_df["deficit_factor"]), 1)
    eval_df["adjusted_amount"]    = np.clip(eval_df["raw_recommendation"] - eval_df["rain_adjustment"], 0, None)
    eval_df["total_litres"]       = np.round(eval_df["adjusted_amount"] * eval_df["area_acres"] * 4046.86 / 1000, 1)  # mm → litres

    # Confidence score: higher when data is more decisive
    eval_df["confidence"] = np.clip(
        50 + abs(eval_df["moisture"] - eval_df["threshold"]) + (eval_df["rain_prob"] / 5),
        0, 100,
    ).round(0)

    row = eval_df.iloc[0]

    # ── Decision tree ────────────────────────────────────────────────
    if row["is_moist_enough"]:
        return _build_response(
            recommendation="wait",
            amount_mm=0,
            total_litres=0,
            reason=(
                f"Soil moisture ({moisture_percent:.1f}%) is at or above the "
                f"{threshold:.0f}% threshold for this growth stage. "
                f"No irrigation needed."
            ),
            moisture_percent=moisture_percent,
            threshold_percent=threshold,
            deficit_factor=0,
            rain_adjustment_mm=0,
            confidence_score=int(row["confidence"]),
        )

    if row["rain_covers_need"]:
        return _build_response(
            recommendation="wait",
            amount_mm=0,
            total_litres=0,
            reason=(
                f"High rain probability ({rain_probability_percent:.0f}%) with "
                f"expected {expected_rainfall_mm:.1f} mm rainfall — sufficient "
                f"to cover ≥70% of the {daily_need:.1f} mm daily need."
            ),
            moisture_percent=moisture_percent,
            threshold_percent=threshold,
            deficit_factor=round(float(row["deficit_factor"]), 3),
            rain_adjustment_mm=round(float(row["rain_adjustment"]), 1),
            confidence_score=int(row["confidence"]),
        )

    # Irrigate
    amount = round(float(row["adjusted_amount"]), 1)
    litres = round(float(row["total_litres"]), 1)
    
    rain_adj_str = f" (adjusted for {row['rain_adjustment']:.1f} mm expected rain)" if row['rain_adjustment'] > 0 else ""
    
    return _build_response(
        recommendation="irrigate",
        amount_mm=amount,
        total_litres=litres,
        reason=(
            f"Soil moisture ({moisture_percent:.1f}%) is below the {threshold:.0f}% "
            f"threshold. Recommended {amount} mm irrigation{rain_adj_str}."
        ),
        moisture_percent=moisture_percent,
        threshold_percent=threshold,
        deficit_factor=round(float(row["deficit_factor"]), 3),
        rain_adjustment_mm=round(float(row["rain_adjustment"]), 1),
        confidence_score=int(row["confidence"]),
    )


def evaluate_batch(readings: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Evaluate multiple moisture readings at once (batch advisory).
    Returns a DataFrame with recommendation for each reading.
    Useful for admin dashboards and scheduled advisory runs.
    """
    results = []
    for r in readings:
        rule = lookup_crop_rule(r.get("crop_type", ""), r.get("growth_stage", ""))
        if rule is None:
            rule = {"moisture_threshold_percent": 50, "water_requirement_mm_per_day": 10}
        rec = get_recommendation(
            moisture_percent=r.get("moisture_percent", 0),
            crop_stage_rule=rule,
            rain_probability_percent=r.get("rain_probability_percent", 0),
            expected_rainfall_mm=r.get("expected_rainfall_mm", 0),
            field_area_acres=r.get("area_acres", 1),
        )
        rec["field_id"] = r.get("field_id", "")
        results.append(rec)
    return pd.DataFrame(results)


# ── Internal helper ──────────────────────────────────────────────────
def _build_response(**kwargs) -> Dict[str, Any]:
    """Standardised response envelope."""
    return {k: v for k, v in kwargs.items()}
