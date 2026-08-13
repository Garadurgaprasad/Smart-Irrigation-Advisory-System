"""
advisory_engine.py — Advanced Multi-Factor Irrigation Advisory Engine
═════════════════════════════════════════════════════════════════════
Smart Irrigation Advisory System · Hackathon Backend & Core Engine

Comprehensive agronomic engine combining:
  1. Crop Agronomy (16+ crops, stage-by-stage Kc, root depth, depletion fraction)
  2. Soil Hydrodynamics (Field Capacity, Wilting Point, Available Water Capacity)
  3. Atmospheric Evapotranspiration (ET0 & ETc = Kc * ET0)
  4. Effective Precipitation Modeling (Peff)
  5. Irrigation System Application Efficiencies (Drip, Sprinkler, Furrow, Flood)
  6. Pump Run-Time & Volume Dynamics (HP / flow rate -> exact operating hours)
  7. 7-Day Predictive Soil Water Balance Simulation
  8. Agro-Advisory Risk Alerts (Disease risk, heat stress, fertigation timing)
  9. Multi-Language Farmer Bulletins (English, Hindi, Telugu)
"""

import math
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════════════════
# 1 · CROP AGRONOMIC REFERENCE DATABASE (FAO-56 Grounded)
# ═══════════════════════════════════════════════════════════════════════

CROP_RULES_DATA = [
    # Rice (Paddy)
    {"crop_type": "Rice", "growth_stage": "Germination",  "kc": 1.05, "water_requirement_mm_per_day": 8.0,  "moisture_threshold_percent": 65.0, "root_depth_cm": 20, "depletion_p": 0.20, "stage_days": 15},
    {"crop_type": "Rice", "growth_stage": "Vegetative",   "kc": 1.15, "water_requirement_mm_per_day": 10.0, "moisture_threshold_percent": 55.0, "root_depth_cm": 45, "depletion_p": 0.20, "stage_days": 40},
    {"crop_type": "Rice", "growth_stage": "Flowering",    "kc": 1.25, "water_requirement_mm_per_day": 12.0, "moisture_threshold_percent": 60.0, "root_depth_cm": 60, "depletion_p": 0.15, "stage_days": 30},
    {"crop_type": "Rice", "growth_stage": "Maturity",     "kc": 0.90, "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 45.0, "root_depth_cm": 60, "depletion_p": 0.35, "stage_days": 25},

    # Wheat
    {"crop_type": "Wheat", "growth_stage": "Germination",  "kc": 0.40, "water_requirement_mm_per_day": 3.0,  "moisture_threshold_percent": 50.0, "root_depth_cm": 25, "depletion_p": 0.55, "stage_days": 15},
    {"crop_type": "Wheat", "growth_stage": "Vegetative",   "kc": 0.85, "water_requirement_mm_per_day": 5.5,  "moisture_threshold_percent": 45.0, "root_depth_cm": 60, "depletion_p": 0.55, "stage_days": 35},
    {"crop_type": "Wheat", "growth_stage": "Flowering",    "kc": 1.15, "water_requirement_mm_per_day": 7.5,  "moisture_threshold_percent": 55.0, "root_depth_cm": 90, "depletion_p": 0.45, "stage_days": 30},
    {"crop_type": "Wheat", "growth_stage": "Maturity",     "kc": 0.50, "water_requirement_mm_per_day": 3.5,  "moisture_threshold_percent": 38.0, "root_depth_cm": 100, "depletion_p": 0.65, "stage_days": 30},

    # Maize (Corn)
    {"crop_type": "Maize", "growth_stage": "Germination", "kc": 0.45, "water_requirement_mm_per_day": 4.0,  "moisture_threshold_percent": 55.0, "root_depth_cm": 25, "depletion_p": 0.55, "stage_days": 15},
    {"crop_type": "Maize", "growth_stage": "Vegetative",  "kc": 0.85, "water_requirement_mm_per_day": 7.5,  "moisture_threshold_percent": 50.0, "root_depth_cm": 60, "depletion_p": 0.50, "stage_days": 35},
    {"crop_type": "Maize", "growth_stage": "Flowering",   "kc": 1.20, "water_requirement_mm_per_day": 10.0, "moisture_threshold_percent": 55.0, "root_depth_cm": 100, "depletion_p": 0.40, "stage_days": 35},
    {"crop_type": "Maize", "growth_stage": "Maturity",    "kc": 0.60, "water_requirement_mm_per_day": 5.0,  "moisture_threshold_percent": 40.0, "root_depth_cm": 100, "depletion_p": 0.60, "stage_days": 25},

    # Chili (Hot Pepper)
    {"crop_type": "Chili", "growth_stage": "Germination", "kc": 0.50, "water_requirement_mm_per_day": 4.5,  "moisture_threshold_percent": 60.0, "root_depth_cm": 20, "depletion_p": 0.30, "stage_days": 20},
    {"crop_type": "Chili", "growth_stage": "Vegetative",  "kc": 0.80, "water_requirement_mm_per_day": 6.5,  "moisture_threshold_percent": 50.0, "root_depth_cm": 45, "depletion_p": 0.35, "stage_days": 40},
    {"crop_type": "Chili", "growth_stage": "Flowering",   "kc": 1.05, "water_requirement_mm_per_day": 9.0,  "moisture_threshold_percent": 55.0, "root_depth_cm": 70, "depletion_p": 0.25, "stage_days": 45},
    {"crop_type": "Chili", "growth_stage": "Maturity",    "kc": 0.75, "water_requirement_mm_per_day": 4.5,  "moisture_threshold_percent": 40.0, "root_depth_cm": 70, "depletion_p": 0.40, "stage_days": 30},

    # Cotton
    {"crop_type": "Cotton", "growth_stage": "Germination", "kc": 0.45, "water_requirement_mm_per_day": 4.0, "moisture_threshold_percent": 55.0, "root_depth_cm": 30, "depletion_p": 0.65, "stage_days": 25},
    {"crop_type": "Cotton", "growth_stage": "Vegetative",  "kc": 0.75, "water_requirement_mm_per_day": 7.0, "moisture_threshold_percent": 48.0, "root_depth_cm": 80, "depletion_p": 0.65, "stage_days": 45},
    {"crop_type": "Cotton", "growth_stage": "Flowering",   "kc": 1.15, "water_requirement_mm_per_day": 9.5, "moisture_threshold_percent": 52.0, "root_depth_cm": 120, "depletion_p": 0.50, "stage_days": 50},
    {"crop_type": "Cotton", "growth_stage": "Maturity",    "kc": 0.65, "water_requirement_mm_per_day": 4.5, "moisture_threshold_percent": 38.0, "root_depth_cm": 130, "depletion_p": 0.70, "stage_days": 40},

    # Sugarcane
    {"crop_type": "Sugarcane", "growth_stage": "Germination", "kc": 0.50, "water_requirement_mm_per_day": 5.5,  "moisture_threshold_percent": 60.0, "root_depth_cm": 30, "depletion_p": 0.65, "stage_days": 35},
    {"crop_type": "Sugarcane", "growth_stage": "Vegetative",  "kc": 1.05, "water_requirement_mm_per_day": 10.0, "moisture_threshold_percent": 55.0, "root_depth_cm": 90, "depletion_p": 0.60, "stage_days": 120},
    {"crop_type": "Sugarcane", "growth_stage": "Flowering",   "kc": 1.25, "water_requirement_mm_per_day": 12.0, "moisture_threshold_percent": 58.0, "root_depth_cm": 150, "depletion_p": 0.50, "stage_days": 90},
    {"crop_type": "Sugarcane", "growth_stage": "Maturity",    "kc": 0.70, "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 42.0, "root_depth_cm": 150, "depletion_p": 0.75, "stage_days": 60},

    # Tomato
    {"crop_type": "Tomato", "growth_stage": "Germination", "kc": 0.50, "water_requirement_mm_per_day": 4.0,  "moisture_threshold_percent": 65.0, "root_depth_cm": 20, "depletion_p": 0.35, "stage_days": 20},
    {"crop_type": "Tomato", "growth_stage": "Vegetative",  "kc": 0.85, "water_requirement_mm_per_day": 6.5,  "moisture_threshold_percent": 55.0, "root_depth_cm": 50, "depletion_p": 0.40, "stage_days": 30},
    {"crop_type": "Tomato", "growth_stage": "Flowering",   "kc": 1.15, "water_requirement_mm_per_day": 9.0,  "moisture_threshold_percent": 60.0, "root_depth_cm": 80, "depletion_p": 0.30, "stage_days": 40},
    {"crop_type": "Tomato", "growth_stage": "Maturity",    "kc": 0.70, "water_requirement_mm_per_day": 5.0,  "moisture_threshold_percent": 45.0, "root_depth_cm": 80, "depletion_p": 0.50, "stage_days": 30},

    # Potato
    {"crop_type": "Potato", "growth_stage": "Germination", "kc": 0.45, "water_requirement_mm_per_day": 3.5,  "moisture_threshold_percent": 60.0, "root_depth_cm": 20, "depletion_p": 0.35, "stage_days": 20},
    {"crop_type": "Potato", "growth_stage": "Vegetative",  "kc": 0.80, "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 55.0, "root_depth_cm": 40, "depletion_p": 0.35, "stage_days": 30},
    {"crop_type": "Potato", "growth_stage": "Flowering",   "kc": 1.15, "water_requirement_mm_per_day": 8.5,  "moisture_threshold_percent": 60.0, "root_depth_cm": 60, "depletion_p": 0.25, "stage_days": 35},
    {"crop_type": "Potato", "growth_stage": "Maturity",    "kc": 0.65, "water_requirement_mm_per_day": 4.0,  "moisture_threshold_percent": 45.0, "root_depth_cm": 60, "depletion_p": 0.45, "stage_days": 25},

    # Groundnut (Peanut)
    {"crop_type": "Groundnut", "growth_stage": "Germination", "kc": 0.40, "water_requirement_mm_per_day": 3.5, "moisture_threshold_percent": 50.0, "root_depth_cm": 25, "depletion_p": 0.50, "stage_days": 20},
    {"crop_type": "Groundnut", "growth_stage": "Vegetative",  "kc": 0.80, "water_requirement_mm_per_day": 6.0, "moisture_threshold_percent": 45.0, "root_depth_cm": 50, "depletion_p": 0.50, "stage_days": 35},
    {"crop_type": "Groundnut", "growth_stage": "Flowering",   "kc": 1.05, "water_requirement_mm_per_day": 8.0, "moisture_threshold_percent": 52.0, "root_depth_cm": 75, "depletion_p": 0.40, "stage_days": 40},
    {"crop_type": "Groundnut", "growth_stage": "Maturity",    "kc": 0.60, "water_requirement_mm_per_day": 4.0, "moisture_threshold_percent": 38.0, "root_depth_cm": 80, "depletion_p": 0.60, "stage_days": 25},

    # Soybean
    {"crop_type": "Soybean", "growth_stage": "Germination", "kc": 0.40, "water_requirement_mm_per_day": 3.5, "moisture_threshold_percent": 55.0, "root_depth_cm": 25, "depletion_p": 0.50, "stage_days": 15},
    {"crop_type": "Soybean", "growth_stage": "Vegetative",  "kc": 0.80, "water_requirement_mm_per_day": 6.0, "moisture_threshold_percent": 48.0, "root_depth_cm": 55, "depletion_p": 0.50, "stage_days": 30},
    {"crop_type": "Soybean", "growth_stage": "Flowering",   "kc": 1.15, "water_requirement_mm_per_day": 8.5, "moisture_threshold_percent": 55.0, "root_depth_cm": 90, "depletion_p": 0.40, "stage_days": 40},
    {"crop_type": "Soybean", "growth_stage": "Maturity",    "kc": 0.55, "water_requirement_mm_per_day": 4.0, "moisture_threshold_percent": 38.0, "root_depth_cm": 90, "depletion_p": 0.60, "stage_days": 25},

    # Onion
    {"crop_type": "Onion", "growth_stage": "Germination", "kc": 0.50, "water_requirement_mm_per_day": 3.5,  "moisture_threshold_percent": 65.0, "root_depth_cm": 15, "depletion_p": 0.30, "stage_days": 20},
    {"crop_type": "Onion", "growth_stage": "Vegetative",  "kc": 0.85, "water_requirement_mm_per_day": 5.5,  "moisture_threshold_percent": 55.0, "root_depth_cm": 30, "depletion_p": 0.30, "stage_days": 40},
    {"crop_type": "Onion", "growth_stage": "Flowering",   "kc": 1.05, "water_requirement_mm_per_day": 7.5,  "moisture_threshold_percent": 60.0, "root_depth_cm": 45, "depletion_p": 0.25, "stage_days": 35},
    {"crop_type": "Onion", "growth_stage": "Maturity",    "kc": 0.65, "water_requirement_mm_per_day": 3.5,  "moisture_threshold_percent": 40.0, "root_depth_cm": 45, "depletion_p": 0.45, "stage_days": 25},

    # Mustard
    {"crop_type": "Mustard", "growth_stage": "Germination", "kc": 0.35, "water_requirement_mm_per_day": 2.5, "moisture_threshold_percent": 50.0, "root_depth_cm": 20, "depletion_p": 0.60, "stage_days": 15},
    {"crop_type": "Mustard", "growth_stage": "Vegetative",  "kc": 0.75, "water_requirement_mm_per_day": 5.0, "moisture_threshold_percent": 42.0, "root_depth_cm": 50, "depletion_p": 0.60, "stage_days": 35},
    {"crop_type": "Mustard", "growth_stage": "Flowering",   "kc": 1.10, "water_requirement_mm_per_day": 7.0, "moisture_threshold_percent": 48.0, "root_depth_cm": 80, "depletion_p": 0.50, "stage_days": 35},
    {"crop_type": "Mustard", "growth_stage": "Maturity",    "kc": 0.45, "water_requirement_mm_per_day": 3.0, "moisture_threshold_percent": 35.0, "root_depth_cm": 80, "depletion_p": 0.70, "stage_days": 25},

    # Chickpea (Gram)
    {"crop_type": "Chickpea", "growth_stage": "Germination", "kc": 0.35, "water_requirement_mm_per_day": 2.5, "moisture_threshold_percent": 50.0, "root_depth_cm": 25, "depletion_p": 0.60, "stage_days": 15},
    {"crop_type": "Chickpea", "growth_stage": "Vegetative",  "kc": 0.70, "water_requirement_mm_per_day": 4.5, "moisture_threshold_percent": 42.0, "root_depth_cm": 60, "depletion_p": 0.60, "stage_days": 35},
    {"crop_type": "Chickpea", "growth_stage": "Flowering",   "kc": 1.00, "water_requirement_mm_per_day": 6.5, "moisture_threshold_percent": 48.0, "root_depth_cm": 90, "depletion_p": 0.50, "stage_days": 30},
    {"crop_type": "Chickpea", "growth_stage": "Maturity",    "kc": 0.40, "water_requirement_mm_per_day": 2.5, "moisture_threshold_percent": 35.0, "root_depth_cm": 90, "depletion_p": 0.70, "stage_days": 30},

    # Banana
    {"crop_type": "Banana", "growth_stage": "Germination", "kc": 0.65, "water_requirement_mm_per_day": 6.0,  "moisture_threshold_percent": 70.0, "root_depth_cm": 30, "depletion_p": 0.30, "stage_days": 60},
    {"crop_type": "Banana", "growth_stage": "Vegetative",  "kc": 1.00, "water_requirement_mm_per_day": 9.0,  "moisture_threshold_percent": 65.0, "root_depth_cm": 60, "depletion_p": 0.35, "stage_days": 120},
    {"crop_type": "Banana", "growth_stage": "Flowering",   "kc": 1.20, "water_requirement_mm_per_day": 12.0, "moisture_threshold_percent": 68.0, "root_depth_cm": 90, "depletion_p": 0.25, "stage_days": 90},
    {"crop_type": "Banana", "growth_stage": "Maturity",    "kc": 0.95, "water_requirement_mm_per_day": 8.0,  "moisture_threshold_percent": 55.0, "root_depth_cm": 90, "depletion_p": 0.40, "stage_days": 60},
]

CROP_RULES_DF = pd.DataFrame(CROP_RULES_DATA)


# ═══════════════════════════════════════════════════════════════════════
# 2 · SOIL HYDRODYNAMICS REFERENCE
# ═══════════════════════════════════════════════════════════════════════

SOIL_CHARACTERISTICS = {
    "Clay Loam": {
        "field_capacity_pct": 32.0,
        "wilting_point_pct": 15.0,
        "available_water_capacity_mm_per_m": 170.0,
        "infiltration_rate_mm_hr": 10.0,
        "drainage_speed": "Moderate",
        "aeration": "Good",
    },
    "Sandy Loam": {
        "field_capacity_pct": 20.0,
        "wilting_point_pct": 8.0,
        "available_water_capacity_mm_per_m": 120.0,
        "infiltration_rate_mm_hr": 25.0,
        "drainage_speed": "Fast",
        "aeration": "Excellent",
    },
    "Clay": {
        "field_capacity_pct": 40.0,
        "wilting_point_pct": 22.0,
        "available_water_capacity_mm_per_m": 180.0,
        "infiltration_rate_mm_hr": 5.0,
        "drainage_speed": "Slow",
        "aeration": "Poor to Moderate",
    },
    "Sandy": {
        "field_capacity_pct": 12.0,
        "wilting_point_pct": 4.0,
        "available_water_capacity_mm_per_m": 80.0,
        "infiltration_rate_mm_hr": 50.0,
        "drainage_speed": "Very Fast",
        "aeration": "High",
    },
    "Silt Loam": {
        "field_capacity_pct": 30.0,
        "wilting_point_pct": 11.0,
        "available_water_capacity_mm_per_m": 190.0,
        "infiltration_rate_mm_hr": 15.0,
        "drainage_speed": "Moderate",
        "aeration": "Good",
    },
    "Vertisol (Black Soil)": {
        "field_capacity_pct": 42.0,
        "wilting_point_pct": 20.0,
        "available_water_capacity_mm_per_m": 220.0,
        "infiltration_rate_mm_hr": 4.0,
        "drainage_speed": "Slow",
        "aeration": "Moderate",
    },
    "Red Soil": {
        "field_capacity_pct": 24.0,
        "wilting_point_pct": 10.0,
        "available_water_capacity_mm_per_m": 140.0,
        "infiltration_rate_mm_hr": 20.0,
        "drainage_speed": "Moderate-Fast",
        "aeration": "Good",
    },
    "Alluvial": {
        "field_capacity_pct": 28.0,
        "wilting_point_pct": 12.0,
        "available_water_capacity_mm_per_m": 160.0,
        "infiltration_rate_mm_hr": 18.0,
        "drainage_speed": "Moderate",
        "aeration": "Good",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# 3 · IRRIGATION METHOD EFFICIENCIES
# ═══════════════════════════════════════════════════════════════════════

IRRIGATION_METHODS = {
    "Drip": {
        "efficiency": 0.90,
        "evaporation_loss_pct": 5,
        "uniformity": 0.92,
        "recommended_for": ["Chili", "Tomato", "Cotton", "Sugarcane", "Banana", "Onion"],
    },
    "Sprinkler": {
        "efficiency": 0.75,
        "evaporation_loss_pct": 15,
        "uniformity": 0.82,
        "recommended_for": ["Wheat", "Maize", "Groundnut", "Mustard", "Potato"],
    },
    "Furrow": {
        "efficiency": 0.60,
        "evaporation_loss_pct": 25,
        "uniformity": 0.70,
        "recommended_for": ["Sugarcane", "Cotton", "Maize", "Potato"],
    },
    "Flood": {
        "efficiency": 0.50,
        "evaporation_loss_pct": 35,
        "uniformity": 0.60,
        "recommended_for": ["Rice"],
    },
}


# ═══════════════════════════════════════════════════════════════════════
# 4 · CORE ADVISORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def lookup_crop_rule(crop_type: str, growth_stage: str) -> Optional[Dict[str, Any]]:
    """
    Look up water requirement and agronomic parameters for crop + stage.
    Case-insensitive matching. Returns None if no exact stage match found.
    """
    if not crop_type or not growth_stage:
        return None

    c_norm = crop_type.strip().lower()
    s_norm = growth_stage.strip().lower()

    mask = (
        (CROP_RULES_DF["crop_type"].str.lower() == c_norm)
        & (CROP_RULES_DF["growth_stage"].str.lower() == s_norm)
    )
    match = CROP_RULES_DF.loc[mask]
    if not match.empty:
        return match.iloc[0].to_dict()

    return None


def calculate_et0(
    temperature_c: float = 30.0,
    humidity_percent: float = 60.0,
    wind_speed_kmh: float = 10.0,
    solar_radiation_mj: float = 20.0,
) -> float:
    """
    Calculate Reference Evapotranspiration (ET0 in mm/day).
    Uses a modified FAO Penman-Monteith / Hargreaves calibrated estimate.
    """
    t_mean = max(-10.0, min(55.0, temperature_c))
    rh_mean = max(10.0, min(100.0, humidity_percent))
    u2 = max(0.5, wind_speed_kmh / 3.6)  # km/h to m/s

    # Saturation vapor pressure (kPa)
    es = 0.6108 * math.exp((17.27 * t_mean) / (t_mean + 237.3))
    ea = es * (rh_mean / 100.0)
    vpd = max(0.0, es - ea)  # Vapor pressure deficit

    # Radiation component
    rad_term = 0.408 * (0.0023 * (t_mean + 17.8) * math.sqrt(max(1.0, 15.0)) * solar_radiation_mj * 0.082)
    # Aerodynamic component
    aero_term = (900 / (t_mean + 273)) * u2 * vpd * 0.25

    et0 = max(1.5, min(12.0, (rad_term + aero_term)))
    return round(et0, 2)


def calculate_effective_rainfall(
    rain_probability_percent: float,
    expected_rainfall_mm: float,
    et_c: float = 6.0,
) -> float:
    """
    Calculate effective rainfall (Peff in mm) that actively contributes
    to soil moisture recharge without runoff loss (USDA SCS method adapted).
    """
    p_prob = max(0.0, min(100.0, rain_probability_percent))
    raw_p = max(0.0, expected_rainfall_mm)

    if p_prob < 30.0 or raw_p <= 0.5:
        return 0.0

    # Weight expected rain by confidence probability
    weighted_rain = raw_p * (p_prob / 100.0)

    # USDA-SCS effective rainfall empirical formula
    if weighted_rain <= 25.0:
        peff = weighted_rain * (1.0 - 0.01 * weighted_rain)
    else:
        peff = 20.0 + 0.6 * (weighted_rain - 25.0)

    # Cap effective rainfall at root capacity
    return round(max(0.0, min(peff, raw_p)), 2)


def calculate_pump_runtime(
    total_litres: float,
    pump_hp: float = 5.0,
    pump_flow_rate_m3_hr: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate pump operating hours, minutes, and energy consumption.
    Standard submersible/monoblock pump: 1 HP ~ 12-15 m3/h at moderate head.
    """
    if total_litres <= 0:
        return {
            "hours": 0,
            "minutes": 0,
            "total_hours": 0.0,
            "total_minutes": 0,
            "flow_rate_lpm": 0,
            "energy_kwh": 0.0,
            "formatted": "0 min",
        }

    # Flow rate estimation
    if pump_flow_rate_m3_hr and pump_flow_rate_m3_hr > 0:
        flow_lpm = (pump_flow_rate_m3_hr * 1000) / 60
    else:
        hp = max(0.5, pump_hp)
        # Average agricultural pump discharge: ~200 Litres/min per HP at 20m head
        flow_lpm = hp * 180.0

    total_minutes = round(total_litres / max(10.0, flow_lpm))
    hrs = int(total_minutes // 60)
    mins = int(total_minutes % 60)
    total_hours = round(total_minutes / 60.0, 2)

    # Energy consumption (kW * hours, motor eff ~ 75%)
    power_kw = (pump_hp * 0.746) / 0.80
    energy_kwh = round(power_kw * total_hours, 2)

    formatted = f"{hrs}h {mins}m" if hrs > 0 else f"{mins} min"

    return {
        "hours": hrs,
        "minutes": mins,
        "total_hours": total_hours,
        "total_minutes": total_minutes,
        "flow_rate_lpm": round(flow_lpm, 1),
        "energy_kwh": energy_kwh,
        "formatted": formatted,
    }


def get_recommendation(
    moisture_percent: float,
    crop_stage_rule: Dict[str, Any],
    rain_probability_percent: float = 0.0,
    expected_rainfall_mm: float = 0.0,
    field_area_acres: float = 1.0,
    soil_type: str = "Clay Loam",
    irrigation_method: str = "Drip",
    temperature_c: float = 30.0,
    humidity_percent: float = 60.0,
    wind_speed_kmh: float = 10.0,
    pump_hp: float = 5.0,
) -> Dict[str, Any]:
    """
    Advanced Multi-Factor Irrigation Recommendation.

    Evaluates:
      - Soil moisture depletion below management allowed depletion (MAD)
      - Crop Evapotranspiration (ETc = Kc * ET0)
      - Effective rainfall forecast credit
      - Irrigation system application efficiency
      - Soil water holding capacity
      - Pump runtime and power requirements
      - Agricultural urgency status and best time of day
    """
    # 1. Extract Crop & Stage parameters
    crop_name = crop_stage_rule.get("crop_type", "General Crop")
    stage_name = crop_stage_rule.get("growth_stage", "Vegetative")
    threshold = float(crop_stage_rule.get("moisture_threshold_percent", 50.0))
    daily_need = float(crop_stage_rule.get("water_requirement_mm_per_day", 8.0))
    kc = float(crop_stage_rule.get("kc", 1.0))
    root_depth_cm = float(crop_stage_rule.get("root_depth_cm", 50.0))
    depletion_p = float(crop_stage_rule.get("depletion_p", 0.50))

    # 2. Extract Soil parameters
    soil_info = SOIL_CHARACTERISTICS.get(soil_type, SOIL_CHARACTERISTICS["Clay Loam"])
    fc = soil_info["field_capacity_pct"]
    pwp = soil_info["wilting_point_pct"]
    awc_mm = soil_info["available_water_capacity_mm_per_m"]

    # Readily Available Water (RAW in mm)
    raw_depth_mm = (awc_mm * (root_depth_cm / 100.0)) * depletion_p

    # 3. Calculate Atmospheric Evapotranspiration (ET0 & ETc)
    et0 = calculate_et0(temperature_c, humidity_percent, wind_speed_kmh)
    etc = round(kc * et0, 2)

    # 4. Calculate Effective Rainfall (Peff)
    peff = calculate_effective_rainfall(rain_probability_percent, expected_rainfall_mm, etc)

    # 5. Application Efficiency
    method_info = IRRIGATION_METHODS.get(irrigation_method, IRRIGATION_METHODS["Drip"])
    eff = method_info["efficiency"]

    # 6. Soil Moisture Deficit Calculation
    current_m = float(moisture_percent)
    deficit_fraction = max(0.0, (threshold - current_m) / max(1.0, threshold))
    
    # Net irrigation needed (mm)
    if current_m >= threshold:
        net_mm = 0.0
    else:
        # Replenish soil root zone deficit + daily crop ETc requirement - expected effective rain
        raw_deficit_mm = (threshold - current_m) * 0.4 * (root_depth_cm / 30.0)
        net_mm = max(0.0, raw_deficit_mm + (etc * 0.5) - peff)

    # Gross mm adjusting for irrigation method application efficiency
    gross_mm = round(net_mm / eff, 1) if net_mm > 0 else 0.0

    # Total volumetric water in litres and m3
    # 1 mm of water over 1 acre = 4,046.86 Litres = 4.047 m3
    litres_per_acre = round(gross_mm * 4046.86, 1)
    total_litres = round(litres_per_acre * field_area_acres, 1)
    total_m3 = round(total_litres / 1000.0, 2)

    # Pump runtime
    pump_specs = calculate_pump_runtime(total_litres, pump_hp=pump_hp)

    # 7. Urgency Status Determination
    status = "ADEQUATE_MOISTURE"
    urgency_badge = "optimal"
    rec_action = "wait"
    reason = ""
    next_window = "Check again tomorrow morning"
    alerts = []

    # Rain condition: high probability and covers significant part of need
    rain_sufficient = (rain_probability_percent >= 55.0 and expected_rainfall_mm >= (0.65 * daily_need))

    if current_m >= threshold:
        status = "ADEQUATE_MOISTURE"
        urgency_badge = "optimal"
        rec_action = "wait"
        reason = (
            f"Soil moisture ({current_m:.1f}%) is within optimal range (threshold: {threshold:.0f}%). "
            f"Crop root zone has sufficient moisture buffer."
        )
        next_window = "Optimal irrigation window in 2-3 days"

    elif rain_sufficient:
        status = "RAIN_EXPECTED_WAIT"
        urgency_badge = "rain_wait"
        rec_action = "wait"
        reason = (
            f"High rain probability ({rain_probability_percent:.0f}%) with expected {expected_rainfall_mm:.1f} mm "
            f"rainfall will satisfy crop water needs ({etc:.1f} mm/day). Hold irrigation to save energy and water."
        )
        alerts.append(f"Estimated water savings: {int(total_litres):,} Litres by utilizing forecast rainfall.")
        next_window = "Re-evaluate after forecast rain event"

    elif current_m > max(threshold, fc) + 8.0:
        status = "EXCESS_WATER_ALERT"
        urgency_badge = "warning"
        rec_action = "wait"
        reason = (
            f"Soil moisture ({current_m:.1f}%) exceeds Field Capacity ({fc:.0f}%). "
            f"Soil is saturated — pause irrigation to avoid waterlogging and root hypoxia."
        )
        alerts.append("High waterlogging risk: Ensure field drainage channels are unobstructed.")

    elif current_m < (threshold - 15.0) or current_m <= (pwp + 5.0):
        status = "IRRIGATE_IMMEDIATELY"
        urgency_badge = "critical"
        rec_action = "irrigate"
        reason = (
            f"Critical moisture deficit: Soil moisture ({current_m:.1f}%) is critically below the "
            f"{threshold:.0f}% threshold near Permanent Wilting Point ({pwp:.0f}%). Apply {gross_mm} mm immediately."
        )
        alerts.append("Crop stress alert: Extended delay will trigger wilting and permanent yield penalty.")
        next_window = "Early Morning (05:00 - 08:30 AM) or Evening (17:30 - 20:00 PM)"

    elif peff > 0.0 and (gross_mm > 0.0):
        status = "IRRIGATE_LIGHT"
        urgency_badge = "recommended"
        rec_action = "irrigate"
        reason = (
            f"Soil moisture ({current_m:.1f}%) is below threshold ({threshold:.0f}%). "
            f"Applying {gross_mm} mm top-up irrigation (credited for {peff:.1f} mm expected rain)."
        )
        next_window = "Early Morning (05:30 - 08:00 AM) to minimize midday evaporation"

    else:
        status = "IRRIGATE_TODAY"
        urgency_badge = "recommended"
        rec_action = "irrigate"
        reason = (
            f"Soil moisture ({current_m:.1f}%) is below {threshold:.0f}% target for {stage_name} stage. "
            f"Recommended irrigation of {gross_mm} mm ({int(total_litres):,} Litres)."
        )
        next_window = "Early Morning (05:30 - 08:30 AM) or Late Evening"

    # Heat Stress & Disease Alerts
    if temperature_c >= 38.0:
        alerts.append("Extreme Heat Stress: Consider short cooling pulse to reduce canopy temperature.")
    if humidity_percent >= 80.0 and current_m >= threshold:
        alerts.append("Fungal Disease Watch: High humidity + moist soil creates fungal susceptibility.")

    # Confidence calculation
    confidence = int(np.clip(
        60 + abs(current_m - threshold) * 1.2 + (rain_probability_percent * 0.15),
        50, 99
    ))

    # Generate Multi-Language Bulletin
    bulletins = _generate_multilingual_bulletin(
        crop=crop_name,
        stage=stage_name,
        action=rec_action,
        status=status,
        amount_mm=gross_mm,
        litres=total_litres,
        pump_time=pump_specs["formatted"],
        current_m=current_m,
        threshold=threshold,
    )

    return {
        # Core backward-compatible fields
        "recommendation": rec_action,
        "amount_mm": gross_mm,
        "total_litres": total_litres,
        "reason": reason,
        "moisture_percent": current_m,
        "threshold_percent": threshold,
        "deficit_factor": round(deficit_fraction, 3),
        "rain_adjustment_mm": peff,
        "confidence_score": confidence,

        # Advanced agronomic fields
        "status": status,
        "urgency_badge": urgency_badge,
        "net_amount_mm": round(net_mm, 1),
        "gross_amount_mm": gross_mm,
        "total_m3": total_m3,
        "field_area_acres": field_area_acres,
        "irrigation_method": irrigation_method,
        "system_efficiency_pct": int(eff * 100),
        "crop_coefficient_kc": kc,
        "reference_et0_mm_day": et0,
        "crop_etc_mm_day": etc,
        "effective_rainfall_mm": peff,
        "soil_type": soil_type,
        "field_capacity_pct": fc,
        "wilting_point_pct": pwp,
        "root_depth_cm": root_depth_cm,
        "readily_available_water_mm": round(raw_depth_mm, 1),
        "pump_runtime": pump_specs,
        "recommended_window": next_window,
        "alerts": alerts,
        "bulletins": bulletins,
    }


def generate_7day_schedule(
    crop_type: str,
    growth_stage: str,
    initial_moisture_pct: float,
    soil_type: str = "Clay Loam",
    irrigation_method: str = "Drip",
    field_area_acres: float = 1.0,
    pump_hp: float = 5.0,
    forecast_days: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Project a 7-day forward soil moisture and irrigation schedule forecast.
    Simulates daily crop ETc consumption, weather events, and irrigation triggers.
    """
    rule = lookup_crop_rule(crop_type, growth_stage) or {
        "moisture_threshold_percent": 50.0,
        "water_requirement_mm_per_day": 8.0,
        "kc": 1.0,
        "root_depth_cm": 50,
        "depletion_p": 0.5,
    }
    threshold = float(rule.get("moisture_threshold_percent", 50.0))
    kc = float(rule.get("kc", 1.0))
    soil = SOIL_CHARACTERISTICS.get(soil_type, SOIL_CHARACTERISTICS["Clay Loam"])
    eff = IRRIGATION_METHODS.get(irrigation_method, IRRIGATION_METHODS["Drip"])["efficiency"]

    today = datetime.date.today()
    simulated_moisture = float(initial_moisture_pct)
    schedule = []

    # Default forecast if none provided
    if not forecast_days or len(forecast_days) < 7:
        forecast_days = [
            {"day_offset": i, "temp_c": 32 + (i % 3), "humidity_pct": 55 - (i % 5), "rain_prob": 10 if i not in [2, 3] else 45, "exp_rain_mm": 0.0 if i not in [2, 3] else 6.0}
            for i in range(7)
        ]

    for idx, f in enumerate(forecast_days[:7]):
        date_str = (today + datetime.timedelta(days=idx)).strftime("%a, %b %d")
        temp = float(f.get("temp_c", 30))
        hum = float(f.get("humidity_pct", 60))
        rain_prob = float(f.get("rain_prob", 10))
        rain_mm = float(f.get("exp_rain_mm", 0))

        # Daily ETc
        et0 = calculate_et0(temp, hum)
        etc = round(kc * et0, 1)

        # Effective rain
        peff = calculate_effective_rainfall(rain_prob, rain_mm, etc)

        # Moisture dynamics (approx 1mm water ~ 0.4% soil moisture change in 50cm root zone)
        moisture_gain = peff * 0.4
        moisture_loss = etc * 0.4
        projected_before_irr = max(10.0, min(soil["field_capacity_pct"] + 5, simulated_moisture + moisture_gain - moisture_loss))

        # Check if irrigation triggered
        if projected_before_irr < threshold and (rain_prob < 50.0 or rain_mm < (etc * 0.5)):
            req_mm = round(((threshold + 5.0) - projected_before_irr) * 2.5 / eff, 1)
            action = "IRRIGATE"
            water_litres = round(req_mm * 4046.86 * field_area_acres, 0)
            pump_time = calculate_pump_runtime(water_litres, pump_hp=pump_hp)["formatted"]
            simulated_moisture = threshold + 5.0  # Reset after irrigation
        else:
            req_mm = 0.0
            action = "WAIT" if rain_prob >= 50 else "ADEQUATE"
            water_litres = 0
            pump_time = "0 min"
            simulated_moisture = projected_before_irr

        schedule.append({
            "day": idx + 1,
            "date": date_str,
            "temp_c": temp,
            "humidity_pct": hum,
            "rain_prob_pct": rain_prob,
            "expected_rain_mm": rain_mm,
            "crop_etc_mm": etc,
            "effective_rain_mm": peff,
            "projected_moisture_pct": round(projected_before_irr, 1),
            "threshold_pct": threshold,
            "action": action,
            "water_mm": req_mm,
            "water_litres": int(water_litres),
            "pump_runtime": pump_time,
        })

    return schedule


def evaluate_batch(readings: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Batch evaluation across multiple fields. Returns standard DataFrame.
    """
    results = []
    for r in readings:
        rule = lookup_crop_rule(r.get("crop_type", ""), r.get("growth_stage", ""))
        if rule is None:
            rule = {"moisture_threshold_percent": 50, "water_requirement_mm_per_day": 8, "kc": 1.0}

        rec = get_recommendation(
            moisture_percent=r.get("moisture_percent", 0),
            crop_stage_rule=rule,
            rain_probability_percent=r.get("rain_probability_percent", 0),
            expected_rainfall_mm=r.get("expected_rainfall_mm", 0),
            field_area_acres=r.get("area_acres", 1.0),
            soil_type=r.get("soil_type", "Clay Loam"),
            irrigation_method=r.get("irrigation_method", "Drip"),
            temperature_c=r.get("temperature_c", 30.0),
            humidity_percent=r.get("humidity_percent", 60.0),
            pump_hp=r.get("pump_hp", 5.0),
        )
        rec["field_id"] = r.get("field_id", "")
        rec["field_name"] = r.get("name", r.get("field_name", "Field"))
        results.append(rec)

    return pd.DataFrame(results)


# ═══════════════════════════════════════════════════════════════════════
# 5 · MULTI-LANGUAGE BULLETIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def _generate_multilingual_bulletin(
    crop: str,
    stage: str,
    action: str,
    status: str,
    amount_mm: float,
    litres: float,
    pump_time: str,
    current_m: float,
    threshold: float,
) -> Dict[str, str]:
    """
    Generate instant localized advisory bulletins in English, Hindi, and Telugu.
    """
    if action == "irrigate":
        en = (
            f"🌾 AgriSense Advisory for {crop} ({stage}): "
            f"Soil moisture is {current_m:.1f}% (threshold {threshold:.0f}%). "
            f"Irrigate with {amount_mm} mm ({int(litres):,} L). "
            f"Estimated pump runtime: {pump_time}."
        )
        hi = (
            f"🌾 एग्रीसेंस सलाह ({crop} - {stage}): "
            f"मिट्टी की नमी {current_m:.1f}% है (न्यूनतम सीमा {threshold:.0f}%)। "
            f"अनुशंसित सिंचाई: {amount_mm} मिमी ({int(litres):,} लीटर)। "
            f"पंप चलाने का समय: {pump_time}।"
        )
        te = (
            f"🌾 అగ్రిసెన్స్ సలహా ({crop} - {stage}): "
            f"నేల తేమ {current_m:.1f}% గా ఉంది (పరిమితి {threshold:.0f}%)। "
            f"సిఫార్సు చేసిన నీటి పరిమాణం: {amount_mm} మి.మీ ({int(litres):,} లీటర్లు)। "
            f"మోటార్ నడిపే సమయం: {pump_time}."
        )
    else:
        en = (
            f"🌾 AgriSense Advisory for {crop} ({stage}): "
            f"Soil moisture ({current_m:.1f}%) is adequate or rain is forecast. "
            f"No irrigation required at this time. Water saved: {int(litres):,} L."
        )
        hi = (
            f"🌾 एग्रीसेंस सलाह ({crop} - {stage}): "
            f"मिट्टी में पर्याप्त नमी ({current_m:.1f}%) है या वर्षा संभावित है। "
            f"फिलहाल सिंचाई की आवश्यकता नहीं है।"
        )
        te = (
            f"🌾 అగ్రిసెన్స్ సలహా ({crop} - {stage}): "
            f"నేలలో తగినంత తేమ ({current_m:.1f}%) ఉంది లేదా వర్ష సూచన ఉంది। "
            f"ప్రస్తుతానికి నీటిపారుదల అవసరం లేదు."
        )

    return {"en": en, "hi": hi, "te": te}
