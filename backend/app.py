"""
app.py — Smart Irrigation Advisory System · Flask REST API
═══════════════════════════════════════════════════════════
Production-grade backend combining:
  • Python Flask         (required by hackathon)
  • Firebase Firestore   (persistent NoSQL storage)
  • Firebase Auth        (user authentication)
  • Pandas               (data analytics — required)
  • Matplotlib / Plotly   (visualization — required)
  • JWT                  (stateless API auth tokens)

Runs in two modes:
  1. FIREBASE MODE — connects to real Firestore (when credentials are set)
  2. LOCAL DEMO MODE — in-memory dict storage (for hackathon demo)
"""

import os
import json
import uuid
import random
import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
import requests as http_requests

# Analytics & Advisory Engine
from advisory_engine import get_recommendation, lookup_crop_rule, evaluate_batch, CROP_RULES_DF
from analytics import (
    compute_water_usage_trend,
    compute_adherence,
    compute_moisture_trend,
    generate_water_usage_chart,
    generate_adherence_chart,
    generate_moisture_chart,
    generate_plotly_water_usage,
    generate_plotly_adherence,
    generate_plotly_moisture,
)


# ═══════════════════════════════════════════════════════════════════════
# APP CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
app = Flask(__name__, static_folder=frontend_dir, static_url_path='/')
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "smart-irrigation-jwt-secret-2024")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=24)
jwt = JWTManager(app)


# ═══════════════════════════════════════════════════════════════════════
# FIREBASE / DEMO-MODE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

FIREBASE_MODE = False
db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth as firebase_auth

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        FIREBASE_MODE = True
        print("SUCCESS: Firebase initialized — running in FIREBASE MODE")
    else:
        print("INFO: No Firebase credentials — running in LOCAL DEMO MODE")
except ImportError:
    print("INFO: firebase-admin not installed — running in LOCAL DEMO MODE")
except Exception as exc:
    print(f"WARNING: Firebase init failed ({exc}) — falling back to LOCAL DEMO MODE")


# ═══════════════════════════════════════════════════════════════════════
# IN-MEMORY MOCK DATABASE (Local Demo Mode)
# ═══════════════════════════════════════════════════════════════════════

MOCK_DB_FILE = os.path.join(os.path.dirname(__file__), "mock_db.json")

def _generate_id() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _load_mock_db() -> dict:
    """Load or initialize the in-memory database with demo data."""
    default = {
        "users": {},
        "fields": {},
        "moisture_logs": {},
        "irrigation_logs": {},
        "weather_cache": {},
        "rules": {},
    }
    if os.path.exists(MOCK_DB_FILE):
        try:
            with open(MOCK_DB_FILE, "r") as f:
                data = json.load(f)
                for k in default:
                    if k not in data:
                        data[k] = default[k]
                return data
        except Exception:
            pass
    return default


def _save_mock_db():
    """Persist mock DB to disk."""
    try:
        with open(MOCK_DB_FILE, "w") as f:
            json.dump(mock_db, f, indent=2, default=str)
    except Exception as e:
        print(f"Warning: Could not save mock DB: {e}")


mock_db = _load_mock_db()

# Seed demo data if empty
if not FIREBASE_MODE and not mock_db["users"]:
    from seed_data import seed_mock_db
    mock_db = seed_mock_db(mock_db)
    _save_mock_db()
    print("Seeded demo data into mock database")


# ═══════════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════════════

def admin_required(fn):
    """Decorator: endpoint requires admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get("role") != "admin":
            return jsonify({"error": "Admin access required", "code": "FORBIDDEN"}), 403
        return fn(*args, **kwargs)
    return wrapper


# ═══════════════════════════════════════════════════════════════════════
# FIRESTORE HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _fs_get_collection(path: str, filters=None, order_by=None, limit=None):
    """Query a Firestore collection with optional filters."""
    ref = db.collection(path)
    if filters:
        for field, op, value in filters:
            ref = ref.where(field, op, value)
    if order_by:
        ref = ref.order_by(order_by[0], direction=order_by[1])
    if limit:
        ref = ref.limit(limit)
    return [{**doc.to_dict(), "id": doc.id} for doc in ref.stream()]


def _fs_get_subcollection(parent_path: str, doc_id: str, subcol: str, order_by=None, limit=None):
    """Query a Firestore subcollection."""
    ref = db.collection(parent_path).document(doc_id).collection(subcol)
    if order_by:
        ref = ref.order_by(order_by[0], direction=order_by[1])
    if limit:
        ref = ref.limit(limit)
    return [{**doc.to_dict(), "id": doc.id} for doc in ref.stream()]


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user (farmer or admin)."""
    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name     = data.get("name", "").strip()
    role     = data.get("role", "farmer").strip().lower()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if role not in ("farmer", "admin"):
        return jsonify({"error": "Role must be 'farmer' or 'admin'"}), 400

    if FIREBASE_MODE:
        try:
            # Create in Firebase Auth
            user_record = firebase_auth.create_user(email=email, password=password, display_name=name)
            firebase_auth.set_custom_user_claims(user_record.uid, {"role": role})
            # Store profile in Firestore
            db.collection("users").document(user_record.uid).set({
                "email": email, "name": name, "role": role,
                "created_at": firestore.SERVER_TIMESTAMP,
            })
            identity = {"uid": user_record.uid, "email": email, "name": name, "role": role}
            token = create_access_token(identity=identity)
            return jsonify({"token": token, "user": identity}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        # Demo mode
        for uid, u in mock_db["users"].items():
            if u["email"] == email:
                return jsonify({"error": "Email already registered"}), 409
        uid = _generate_id()
        mock_db["users"][uid] = {
            "email": email,
            "name": name or email.split("@")[0],
            "role": role,
            "password_hash": generate_password_hash(password),
            "created_at": _now_iso(),
        }
        _save_mock_db()
        identity = {"uid": uid, "email": email, "name": name, "role": role}
        token = create_access_token(identity=identity)
        return jsonify({"token": token, "user": identity}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT."""
    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if FIREBASE_MODE:
        api_key = os.environ.get("FIREBASE_API_KEY", "")
        if not api_key:
            return jsonify({"error": "FIREBASE_API_KEY not configured"}), 500
        try:
            resp = http_requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
                json={"email": email, "password": password, "returnSecureToken": True},
                timeout=10,
            )
            if resp.status_code != 200:
                err_msg = resp.json().get("error", {}).get("message", "Authentication failed")
                return jsonify({"error": err_msg}), 401

            fb_data = resp.json()
            uid = fb_data["localId"]
            user_doc = db.collection("users").document(uid).get()
            role = user_doc.to_dict().get("role", "farmer") if user_doc.exists else "farmer"
            name = user_doc.to_dict().get("name", "") if user_doc.exists else ""

            identity = {"uid": uid, "email": email, "name": name, "role": role}
            token = create_access_token(identity=identity)
            return jsonify({"token": token, "user": identity}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Demo mode
        for uid, u in mock_db["users"].items():
            if u["email"] == email:
                if check_password_hash(u["password_hash"], password):
                    identity = {"uid": uid, "email": email, "name": u.get("name", ""), "role": u["role"]}
                    token = create_access_token(identity=identity)
                    return jsonify({"token": token, "user": identity}), 200
                else:
                    return jsonify({"error": "Invalid password"}), 401
        return jsonify({"error": "User not found"}), 404


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def auth_me():
    """Return current authenticated user."""
    return jsonify({"user": get_jwt_identity()}), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — FIELDS (CRUD)
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/fields", methods=["GET"])
@jwt_required()
def list_fields():
    """List all fields belonging to the authenticated user."""
    user = get_jwt_identity()
    uid = user["uid"]

    if FIREBASE_MODE:
        fields = _fs_get_collection("fields", filters=[("user_id", "==", uid)])
        return jsonify(fields), 200
    else:
        result = []
        for fid, f in mock_db["fields"].items():
            if f.get("user_id") == uid:
                result.append({"id": fid, **f})
        return jsonify(result), 200


@app.route("/api/fields", methods=["POST"])
@jwt_required()
def create_field():
    """Create a new field."""
    user = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    field = {
        "name":                 data.get("name", "Unnamed Field"),
        "crop_type":            data.get("crop_type", data.get("crop", "")),
        "area_acres":           float(data.get("area_acres", data.get("area", 1))),
        "current_growth_stage": data.get("current_growth_stage", data.get("growth_stage", "Vegetative")),
        "location":             data.get("location", ""),
        "soil_type":            data.get("soil_type", ""),
        "user_id":              user["uid"],
        "created_at":           _now_iso(),
    }

    if FIREBASE_MODE:
        _, ref = db.collection("fields").add(field)
        return jsonify({"id": ref.id, **field}), 201
    else:
        fid = _generate_id()
        mock_db["fields"][fid] = field
        mock_db["moisture_logs"][fid] = []
        mock_db["irrigation_logs"][fid] = []
        _save_mock_db()
        return jsonify({"id": fid, **field}), 201


@app.route("/api/fields/<field_id>", methods=["GET"])
@jwt_required()
def get_field(field_id):
    """Get a single field by ID."""
    if FIREBASE_MODE:
        doc = db.collection("fields").document(field_id).get()
        if not doc.exists:
            return jsonify({"error": "Field not found"}), 404
        return jsonify({"id": doc.id, **doc.to_dict()}), 200
    else:
        field = mock_db["fields"].get(field_id)
        if not field:
            return jsonify({"error": "Field not found"}), 404
        return jsonify({"id": field_id, **field}), 200


@app.route("/api/fields/<field_id>", methods=["PUT"])
@jwt_required()
def update_field(field_id):
    """Update a field (e.g. change growth stage)."""
    data = request.get_json(silent=True) or {}

    if FIREBASE_MODE:
        ref = db.collection("fields").document(field_id)
        if not ref.get().exists:
            return jsonify({"error": "Field not found"}), 404
        ref.update(data)
        updated = ref.get().to_dict()
        return jsonify({"id": field_id, **updated}), 200
    else:
        if field_id not in mock_db["fields"]:
            return jsonify({"error": "Field not found"}), 404
        mock_db["fields"][field_id].update(data)
        _save_mock_db()
        return jsonify({"id": field_id, **mock_db["fields"][field_id]}), 200


@app.route("/api/fields/<field_id>", methods=["DELETE"])
@jwt_required()
def delete_field(field_id):
    """Delete a field and its sub-data."""
    if FIREBASE_MODE:
        ref = db.collection("fields").document(field_id)
        if not ref.get().exists:
            return jsonify({"error": "Field not found"}), 404
        ref.delete()
        return jsonify({"message": "Field deleted"}), 200
    else:
        if field_id not in mock_db["fields"]:
            return jsonify({"error": "Field not found"}), 404
        del mock_db["fields"][field_id]
        mock_db["moisture_logs"].pop(field_id, None)
        mock_db["irrigation_logs"].pop(field_id, None)
        _save_mock_db()
        return jsonify({"message": "Field deleted"}), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — SOIL MOISTURE
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/fields/<field_id>/moisture", methods=["POST"])
@jwt_required()
def log_moisture(field_id):
    """Log a soil moisture reading for a field."""
    data = request.get_json(silent=True) or {}
    reading = {
        "moisture_percent": float(data.get("moisture_percent", 0)),
        "source":           data.get("source", "manual"),
        "timestamp":        _now_iso(),
    }

    if FIREBASE_MODE:
        _, ref = db.collection("fields").document(field_id).collection("moistureReadings").add(reading)
        return jsonify({"id": ref.id, **reading}), 201
    else:
        if field_id not in mock_db["moisture_logs"]:
            mock_db["moisture_logs"][field_id] = []
        reading["id"] = _generate_id()
        mock_db["moisture_logs"][field_id].append(reading)
        _save_mock_db()
        return jsonify(reading), 201


@app.route("/api/fields/<field_id>/moisture", methods=["GET"])
@jwt_required()
def get_moisture_history(field_id):
    """Get all moisture readings for a field."""
    if FIREBASE_MODE:
        readings = _fs_get_subcollection("fields", field_id, "moistureReadings",
                                          order_by=("timestamp", firestore.Query.DESCENDING))
        return jsonify(readings), 200
    else:
        logs = mock_db["moisture_logs"].get(field_id, [])
        return jsonify(logs), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — WEATHER
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/fields/<field_id>/weather", methods=["GET"])
@jwt_required()
def get_weather(field_id):
    """
    Fetch weather forecast for the field's location.
    Falls back to realistic mock data if no external API is configured.
    """
    weather_api_key = os.environ.get("OPENWEATHER_API_KEY", "")

    if weather_api_key:
        # Real API call to OpenWeatherMap
        try:
            # Get field location
            if FIREBASE_MODE:
                doc = db.collection("fields").document(field_id).get()
                location = doc.to_dict().get("location", "Hyderabad") if doc.exists else "Hyderabad"
            else:
                field = mock_db["fields"].get(field_id, {})
                location = field.get("location", "Hyderabad")

            resp = http_requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": location, "appid": weather_api_key, "units": "metric"},
                timeout=10,
            )
            if resp.status_code == 200:
                w = resp.json()
                weather_data = {
                    "temperature_c":           round(w["main"]["temp"], 1),
                    "humidity_percent":         w["main"]["humidity"],
                    "rain_probability_percent": min(w.get("clouds", {}).get("all", 30), 100),
                    "expected_rainfall_mm":     w.get("rain", {}).get("1h", 0),
                    "wind_speed_kmh":           round(w["wind"]["speed"] * 3.6, 1),
                    "description":             w["weather"][0]["description"] if w.get("weather") else "",
                    "source":                  "openweathermap",
                    "fetched_at":              _now_iso(),
                }
                return jsonify(weather_data), 200
        except Exception:
            pass

    # Realistic mock weather
    weather_data = {
        "temperature_c":           round(random.uniform(24, 38), 1),
        "humidity_percent":        random.randint(40, 85),
        "rain_probability_percent": random.choice([10, 20, 30, 40, 50, 60, 70, 80]),
        "expected_rainfall_mm":    round(random.uniform(0, 15), 1),
        "wind_speed_kmh":          round(random.uniform(5, 25), 1),
        "description":             random.choice(["clear sky", "few clouds", "scattered clouds", "light rain", "overcast"]),
        "source":                  "mock",
        "fetched_at":              _now_iso(),
    }
    return jsonify(weather_data), 200


@app.route("/api/fields/<field_id>/weather", methods=["POST"])
@jwt_required()
def save_weather(field_id):
    """Manually input weather data for a field."""
    data = request.get_json(silent=True) or {}
    weather = {
        "temperature_c":           float(data.get("temperature_c", 30)),
        "humidity_percent":        int(data.get("humidity_percent", 60)),
        "rain_probability_percent": int(data.get("rain_probability_percent", 20)),
        "expected_rainfall_mm":    float(data.get("expected_rainfall_mm", 0)),
        "source":                  "manual",
        "field_id":                field_id,
        "fetched_at":              _now_iso(),
    }

    if FIREBASE_MODE:
        _, ref = db.collection("weather_data").add(weather)
        return jsonify({"id": ref.id, **weather}), 201
    else:
        if field_id not in mock_db["weather_cache"]:
            mock_db["weather_cache"][field_id] = []
        weather["id"] = _generate_id()
        mock_db["weather_cache"][field_id].append(weather)
        _save_mock_db()
        return jsonify(weather), 201


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — ADVISORY ENGINE (Core Feature)
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/fields/<field_id>/recommendation", methods=["GET"])
@jwt_required()
def get_field_recommendation(field_id):
    """
    Generate irrigation recommendation for a field.
    Combines latest moisture + weather + crop-stage rules → advisory engine.
    """
    if FIREBASE_MODE:
        field_doc = db.collection("fields").document(field_id).get()
        if not field_doc.exists:
            return jsonify({"error": "Field not found"}), 404
        field_data = field_doc.to_dict()

        # Latest moisture reading
        moisture_docs = list(
            db.collection("fields").document(field_id)
              .collection("moistureReadings")
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .limit(1).stream()
        )
        if not moisture_docs:
            return jsonify({"error": "No moisture readings. Please log soil moisture first."}), 400
        moisture_pct = float(moisture_docs[0].to_dict().get("moisture_percent", 0))

        # Latest weather
        weather_docs = list(
            db.collection("weather_data")
              .where("field_id", "==", field_id)
              .order_by("fetched_at", direction=firestore.Query.DESCENDING)
              .limit(1).stream()
        )
        if weather_docs:
            w = weather_docs[0].to_dict()
            rain_prob = float(w.get("rain_probability_percent", 0))
            exp_rain  = float(w.get("expected_rainfall_mm", 0))
        else:
            rain_prob, exp_rain = 20.0, 0.0

        crop_type = field_data.get("crop_type", "")
        stage     = field_data.get("current_growth_stage", "")

        # Lookup rule from Firestore
        rule_docs = list(
            db.collection("crop_stage_rules")
              .where("crop_type", "==", crop_type)
              .where("growth_stage", "==", stage)
              .stream()
        )
        if rule_docs:
            rule = rule_docs[0].to_dict()
        else:
            rule = lookup_crop_rule(crop_type, stage) or {
                "moisture_threshold_percent": 50,
                "water_requirement_mm_per_day": 10,
            }

        area = float(field_data.get("area_acres", 1))
    else:
        # Demo mode
        field = mock_db["fields"].get(field_id)
        if not field:
            return jsonify({"error": "Field not found"}), 404

        logs = mock_db["moisture_logs"].get(field_id, [])
        if not logs:
            return jsonify({"error": "No moisture readings. Please log soil moisture first."}), 400

        moisture_pct = float(logs[-1]["moisture_percent"])
        crop_type    = field.get("crop_type", field.get("crop", ""))
        stage        = field.get("current_growth_stage", field.get("growth_stage", ""))
        area         = float(field.get("area_acres", field.get("area", 1)))

        # Lookup rule from mock DB or built-in table
        rule = None
        for rid, r in mock_db["rules"].items():
            if (r.get("crop_type", r.get("crop", "")).lower() == crop_type.lower()
                    and r.get("growth_stage", r.get("stage", "")).lower() == stage.lower()):
                rule = r
                break
        if not rule:
            rule = lookup_crop_rule(crop_type, stage) or {
                "moisture_threshold_percent": 50,
                "water_requirement_mm_per_day": 10,
            }

        rain_prob = 30.0
        exp_rain  = round(random.uniform(0, 8), 1)

    rec = get_recommendation(moisture_pct, rule, rain_prob, exp_rain, area)
    rec["weather"] = {
        "rain_probability_percent": rain_prob,
        "expected_rainfall_mm": exp_rain,
    }
    rec["field"] = {
        "crop_type": crop_type,
        "growth_stage": stage,
        "area_acres": area,
    }
    return jsonify(rec), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — IRRIGATION LOGGING
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/fields/<field_id>/irrigate", methods=["POST"])
@jwt_required()
def log_irrigation(field_id):
    """Log an irrigation action (taken or skipped)."""
    data = request.get_json(silent=True) or {}
    log_entry = {
        "recommendation":       data.get("recommendation", "irrigate"),
        "action_taken":         data.get("action_taken", "irrigated"),
        "recommended_amount_mm": float(data.get("recommended_amount_mm", 0)),
        "actual_amount_mm":     float(data.get("actual_amount_mm", 0)),
        "reason":               data.get("reason", ""),
        "date":                 _now_iso(),
        "logged_at":            _now_iso(),
    }

    if FIREBASE_MODE:
        _, ref = db.collection("fields").document(field_id).collection("irrigationLogs").add(log_entry)
        return jsonify({"id": ref.id, **log_entry}), 201
    else:
        if field_id not in mock_db["irrigation_logs"]:
            mock_db["irrigation_logs"][field_id] = []
        log_entry["id"] = _generate_id()
        mock_db["irrigation_logs"][field_id].append(log_entry)
        _save_mock_db()
        return jsonify(log_entry), 201


@app.route("/api/fields/<field_id>/irrigation-logs", methods=["GET"])
@jwt_required()
def get_irrigation_logs(field_id):
    """Get irrigation history for a field."""
    if FIREBASE_MODE:
        logs = _fs_get_subcollection("fields", field_id, "irrigationLogs",
                                      order_by=("logged_at", firestore.Query.DESCENDING))
        return jsonify(logs), 200
    else:
        logs = mock_db["irrigation_logs"].get(field_id, [])
        return jsonify(logs), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — ANALYTICS (Pandas + Matplotlib + Plotly)
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/fields/<field_id>/analytics/water-usage", methods=["GET"])
@jwt_required()
def analytics_water_usage(field_id):
    """
    Water usage trend analysis using Pandas groupby.
    Returns tabular data + Matplotlib base64 chart + Plotly JSON figure.
    """
    period = request.args.get("period", "daily")

    if FIREBASE_MODE:
        logs = _fs_get_subcollection("fields", field_id, "irrigationLogs")
    else:
        logs = mock_db["irrigation_logs"].get(field_id, [])

    trend_data     = compute_water_usage_trend(logs, period=period)
    matplotlib_b64 = generate_water_usage_chart(trend_data)
    plotly_fig     = generate_plotly_water_usage(trend_data)

    return jsonify({
        "data":          trend_data,
        "chart_base64":  matplotlib_b64,
        "plotly_figure":  plotly_fig,
        "period":        period,
        "total_records": len(logs),
    }), 200


@app.route("/api/fields/<field_id>/analytics/adherence", methods=["GET"])
@jwt_required()
def analytics_adherence(field_id):
    """
    Recommendation adherence scoring using Pandas apply.
    Returns stats + Matplotlib chart + Plotly JSON figure.
    """
    if FIREBASE_MODE:
        logs = _fs_get_subcollection("fields", field_id, "irrigationLogs")
    else:
        logs = mock_db["irrigation_logs"].get(field_id, [])

    adherence_data = compute_adherence(logs)
    matplotlib_b64 = generate_adherence_chart(adherence_data)
    plotly_fig     = generate_plotly_adherence(adherence_data)

    return jsonify({
        **adherence_data,
        "chart_base64":  matplotlib_b64,
        "plotly_figure":  plotly_fig,
    }), 200


@app.route("/api/fields/<field_id>/analytics/moisture", methods=["GET"])
@jwt_required()
def analytics_moisture(field_id):
    """
    Moisture trend analysis: rolling average, min/max, trend direction.
    Uses Pandas rolling().mean() for smoothing.
    """
    if FIREBASE_MODE:
        readings = _fs_get_subcollection("fields", field_id, "moistureReadings",
                                          order_by=("timestamp", firestore.Query.ASCENDING))
    else:
        readings = mock_db["moisture_logs"].get(field_id, [])

    moisture_data  = compute_moisture_trend(readings)
    matplotlib_b64 = generate_moisture_chart(moisture_data)
    plotly_fig     = generate_plotly_moisture(moisture_data)

    return jsonify({
        **moisture_data,
        "chart_base64":  matplotlib_b64,
        "plotly_figure":  plotly_fig,
    }), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — ADMIN: CROP-STAGE RULES MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/admin/rules", methods=["GET"])
@jwt_required()
def list_rules():
    """List all crop-stage water requirement rules."""
    if FIREBASE_MODE:
        rules = _fs_get_collection("crop_stage_rules")
        return jsonify(rules), 200
    else:
        result = [{"id": k, **v} for k, v in mock_db["rules"].items()]
        # Also include built-in rules from the advisory engine
        builtin = CROP_RULES_DF.to_dict("records")
        for b in builtin:
            b["id"] = f"builtin-{b['crop_type']}-{b['growth_stage']}".lower()
            b["source"] = "builtin"
        return jsonify(result + builtin), 200


@app.route("/api/admin/rules", methods=["POST"])
@admin_required
def create_rule():
    """Create a new crop-stage rule."""
    data = request.get_json(silent=True) or {}
    rule = {
        "crop_type":                   data.get("crop_type", data.get("crop", "")),
        "growth_stage":                data.get("growth_stage", data.get("stage", "")),
        "water_requirement_mm_per_day": float(data.get("water_requirement_mm_per_day", 10)),
        "moisture_threshold_percent":  float(data.get("moisture_threshold_percent", 50)),
        "updated_by":                  get_jwt_identity().get("email", ""),
        "updated_at":                  _now_iso(),
    }

    if FIREBASE_MODE:
        _, ref = db.collection("crop_stage_rules").add(rule)
        return jsonify({"id": ref.id, **rule}), 201
    else:
        rid = _generate_id()
        mock_db["rules"][rid] = rule
        _save_mock_db()
        return jsonify({"id": rid, **rule}), 201


@app.route("/api/admin/rules/<rule_id>", methods=["PUT"])
@admin_required
def update_rule(rule_id):
    """Update an existing crop-stage rule."""
    data = request.get_json(silent=True) or {}

    if FIREBASE_MODE:
        ref = db.collection("crop_stage_rules").document(rule_id)
        if not ref.get().exists:
            return jsonify({"error": "Rule not found"}), 404
        data["updated_at"] = _now_iso()
        data["updated_by"] = get_jwt_identity().get("email", "")
        ref.update(data)
        return jsonify({"id": rule_id, **ref.get().to_dict()}), 200
    else:
        if rule_id not in mock_db["rules"]:
            return jsonify({"error": "Rule not found"}), 404
        data["updated_at"] = _now_iso()
        mock_db["rules"][rule_id].update(data)
        _save_mock_db()
        return jsonify({"id": rule_id, **mock_db["rules"][rule_id]}), 200


@app.route("/api/admin/rules/<rule_id>", methods=["DELETE"])
@admin_required
def delete_rule(rule_id):
    """Delete a crop-stage rule."""
    if FIREBASE_MODE:
        ref = db.collection("crop_stage_rules").document(rule_id)
        if not ref.get().exists:
            return jsonify({"error": "Rule not found"}), 404
        ref.delete()
        return jsonify({"message": "Rule deleted"}), 200
    else:
        if rule_id not in mock_db["rules"]:
            return jsonify({"error": "Rule not found"}), 404
        del mock_db["rules"][rule_id]
        _save_mock_db()
        return jsonify({"message": "Rule deleted"}), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — BATCH ADVISORY (Bonus Feature)
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/advisory/batch", methods=["POST"])
@jwt_required()
def batch_advisory():
    """
    Evaluate multiple fields at once.
    Useful for admin overview or scheduled advisory runs.
    """
    data = request.get_json(silent=True) or {}
    readings = data.get("readings", [])
    if not readings:
        return jsonify({"error": "No readings provided"}), 400

    results_df = evaluate_batch(readings)
    return jsonify(results_df.to_dict("records")), 200


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES — SYSTEM INFO
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status":        "healthy",
        "mode":          "firebase" if FIREBASE_MODE else "demo",
        "version":       "2.0.0",
        "tech_stack": {
            "backend":       "Python Flask",
            "database":      "Firebase Firestore" if FIREBASE_MODE else "In-Memory (Demo)",
            "analytics":     "Pandas",
            "visualization": "Matplotlib + Plotly",
            "auth":          "JWT + Firebase Auth",
        },
    }), 200


@app.route("/api/crops", methods=["GET"])
def list_crops():
    """List all available crops and growth stages from the advisory engine."""
    crops = (
        CROP_RULES_DF.groupby("crop_type")["growth_stage"]
        .apply(list)
        .to_dict()
    )
    return jsonify(crops), 200


# ═══════════════════════════════════════════════════════════════════════
# STATIC FILE SERVING (Unified server — serves React frontend build)
# ═══════════════════════════════════════════════════════════════════════

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.isdir(FRONTEND_DIR):
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        """Serve React SPA — all non-API routes go to index.html."""
        full_path = os.path.join(FRONTEND_DIR, path)
        if path and os.path.isfile(full_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print(f"\nSmart Irrigation Advisory System — Backend")
    print(f"   Mode:  {'Firebase' if FIREBASE_MODE else 'Local Demo'}")
    print(f"   URL:   http://localhost:{port}")
    print(f"   Docs:  http://localhost:{port}/api/health\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
