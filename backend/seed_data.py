"""
seed_data.py — Demo Data Seeder
════════════════════════════════
Generates realistic demo data for the Smart Irrigation Advisory System.
Called automatically when the backend starts in LOCAL DEMO MODE.
"""

import uuid
import datetime
import random
from werkzeug.security import generate_password_hash


def _id() -> str:
    return str(uuid.uuid4())


def _past_date(days_ago: int) -> str:
    """Generate an ISO timestamp `days_ago` days in the past."""
    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago)
    # Add some random hours
    dt += datetime.timedelta(hours=random.randint(6, 18), minutes=random.randint(0, 59))
    return dt.isoformat()


def seed_mock_db(db: dict) -> dict:
    """
    Populate the mock database with realistic demo data.
    
    Creates:
      • 2 users (farmer + admin)
      • 3 fields for the farmer
      • 15+ moisture readings per field
      • 10+ irrigation logs per field
      • Crop-stage rules for 5 crops × 4 stages
    """

    # ── Users ────────────────────────────────────────────────────────
    farmer_id = _id()
    admin_id  = _id()

    db["users"] = {
        farmer_id: {
            "email":         "farmer@demo.com",
            "name":          "Ravi Kumar",
            "role":          "farmer",
            "password_hash": generate_password_hash("password123"),
            "created_at":    _past_date(60),
        },
        admin_id: {
            "email":         "admin@demo.com",
            "name":          "Dr. Priya Sharma",
            "role":          "admin",
            "password_hash": generate_password_hash("admin123"),
            "created_at":    _past_date(90),
        },
    }

    # ── Fields ───────────────────────────────────────────────────────
    field_1 = _id()
    field_2 = _id()
    field_3 = _id()

    db["fields"] = {
        field_1: {
            "name":                  "Paddy Field North",
            "crop_type":             "Rice",
            "area_acres":            2.5,
            "current_growth_stage":  "Vegetative",
            "location":              "Vijayawada",
            "soil_type":             "Clay Loam",
            "user_id":               farmer_id,
            "created_at":            _past_date(45),
        },
        field_2: {
            "name":                  "Maize Plot East",
            "crop_type":             "Maize",
            "area_acres":            1.8,
            "current_growth_stage":  "Flowering",
            "location":              "Guntur",
            "soil_type":             "Sandy Loam",
            "user_id":               farmer_id,
            "created_at":            _past_date(40),
        },
        field_3: {
            "name":                  "Chili Garden",
            "crop_type":             "Chili",
            "area_acres":            1.2,
            "current_growth_stage":  "Vegetative",
            "location":              "Vizag",
            "soil_type":             "Red Soil",
            "user_id":               farmer_id,
            "created_at":            _past_date(35),
        },
    }

    # ── Moisture Readings (15–20 per field) ──────────────────────────
    db["moisture_logs"] = {}
    for fid in [field_1, field_2, field_3]:
        readings = []
        base_moisture = random.uniform(30, 55)
        for day in range(20, 0, -1):
            # Simulate realistic moisture fluctuation
            base_moisture += random.uniform(-5, 8)
            base_moisture = max(15, min(85, base_moisture))
            readings.append({
                "id":               _id(),
                "moisture_percent":  round(base_moisture, 1),
                "source":           random.choice(["sensor", "manual", "sensor", "sensor"]),
                "timestamp":        _past_date(day),
            })
        db["moisture_logs"][fid] = readings

    # ── Irrigation Logs (10–15 per field) ────────────────────────────
    db["irrigation_logs"] = {}
    actions_map = {
        "irrigate": ["irrigated", "irrigated", "irrigated", "skipped"],  # 75% adherence
        "wait":     ["skipped", "skipped", "skipped", "irrigated"],      # 75% adherence
    }

    for fid in [field_1, field_2, field_3]:
        logs = []
        for day in range(14, 0, -1):
            rec = random.choice(["irrigate", "wait"])
            action = random.choice(actions_map[rec])
            rec_amount = round(random.uniform(4, 14), 1) if rec == "irrigate" else 0
            act_amount = round(rec_amount * random.uniform(0.7, 1.3), 1) if action == "irrigated" else 0

            logs.append({
                "id":                    _id(),
                "recommendation":        rec,
                "action_taken":          action,
                "recommended_amount_mm": rec_amount,
                "actual_amount_mm":      act_amount,
                "reason":                f"Soil moisture {'below' if rec == 'irrigate' else 'above'} threshold",
                "date":                  _past_date(day),
                "logged_at":             _past_date(day),
            })
        db["irrigation_logs"][fid] = logs

    # ── Crop-Stage Rules ─────────────────────────────────────────────
    crops_stages = [
        ("Rice",      "Germination",  8.0,  65.0),
        ("Rice",      "Vegetative",   10.0, 55.0),
        ("Rice",      "Flowering",    12.0, 60.0),
        ("Rice",      "Maturity",     6.0,  45.0),
        ("Maize",     "Germination",  6.0,  55.0),
        ("Maize",     "Vegetative",   8.0,  50.0),
        ("Maize",     "Flowering",    10.0, 55.0),
        ("Maize",     "Maturity",     5.0,  40.0),
        ("Chili",     "Germination",  5.0,  60.0),
        ("Chili",     "Vegetative",   7.0,  50.0),
        ("Chili",     "Flowering",    9.0,  55.0),
        ("Chili",     "Maturity",     4.0,  40.0),
        ("Cotton",    "Germination",  5.5,  55.0),
        ("Cotton",    "Vegetative",   7.5,  48.0),
        ("Cotton",    "Flowering",    9.5,  52.0),
        ("Cotton",    "Maturity",     4.5,  38.0),
        ("Sugarcane", "Germination",  7.0,  60.0),
        ("Sugarcane", "Vegetative",   10.0, 55.0),
        ("Sugarcane", "Flowering",    11.0, 58.0),
        ("Sugarcane", "Maturity",     6.0,  42.0),
    ]

    db["rules"] = {}
    for crop, stage, water_need, threshold in crops_stages:
        rid = _id()
        db["rules"][rid] = {
            "crop_type":                    crop,
            "growth_stage":                 stage,
            "water_requirement_mm_per_day": water_need,
            "moisture_threshold_percent":   threshold,
            "updated_by":                   "admin@demo.com",
            "updated_at":                   _past_date(30),
        }

    # ── Weather Cache ────────────────────────────────────────────────
    db["weather_cache"] = {}

    return db


if __name__ == "__main__":
    import json
    db = {
        "users": {}, "fields": {}, "moisture_logs": {},
        "irrigation_logs": {}, "weather_cache": {}, "rules": {},
    }
    db = seed_mock_db(db)
    with open("mock_db.json", "w") as f:
        json.dump(db, f, indent=2, default=str)
    print(f"✅ Seeded {len(db['users'])} users, {len(db['fields'])} fields, {len(db['rules'])} rules")
    print(f"   Moisture readings: {sum(len(v) for v in db['moisture_logs'].values())}")
    print(f"   Irrigation logs:   {sum(len(v) for v in db['irrigation_logs'].values())}")
