import sys
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace the entire AUTHENTICATION section.
auth_match = re.search(r'# [^\n]*API ROUTES.*?AUTHENTICATION[^\n]*\n# [^\n]*\n+', content)
if not auth_match:
    print('Could not find auth start')
    sys.exit(1)

auth_start = auth_match.start()

fields_match = re.search(r'# [^\n]*API ROUTES.*?FIELDS \(CRUD\)[^\n]*\n# [^\n]*\n+', content)
if not fields_match:
    print('Could not find fields start')
    sys.exit(1)
    
auth_end = fields_match.start()

new_auth = '''# API ROUTES - AUTHENTICATION
# -----------------------------------------------------------------------------

import time

# Simple Memory Rate Limiter
_rate_limits = {}

def rate_limit(key, limit=5, window=60):
    now = time.time()
    if key not in _rate_limits:
        _rate_limits[key] = []
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < window]
    if len(_rate_limits[key]) >= limit:
        return False
    _rate_limits[key].append(now)
    return True

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user."""
    ip = request.remote_addr
    if not rate_limit(f"reg_{ip}", limit=3, window=60):
        return jsonify({"error": "Too many requests"}), 429

    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name     = data.get("name", "").strip()
    role     = data.get("role", "farmer").strip().lower()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if len(password) < 12:
        return jsonify({"error": "Password must be at least 12 characters"}), 400
    if role not in ("farmer", "admin"):
        return jsonify({"error": "Role must be 'farmer' or 'admin'"}), 400

    hashed = generate_password_hash(password)
    verification_token = _generate_id() + _generate_id()

    if FIREBASE_MODE:
        existing = _fs_get_collection("users", filters=[("email", "==", email)], limit=1)
        if existing:
            return jsonify({"message": "If the email is valid, a verification link was sent."}), 200
        
        doc_ref = db.collection("users").document()
        doc_ref.set({
            "email": email, 
            "name": name, 
            "role": role,
            "password_hash": hashed,
            "email_verified": False,
            "created_at": firestore.SERVER_TIMESTAMP,
        })
        db.collection("verification_tokens").document(verification_token).set({
            "user_id": doc_ref.id,
            "created_at": firestore.SERVER_TIMESTAMP,
        })
    else:
        for u_id, u in mock_db["users"].items():
            if u["email"] == email:
                return jsonify({"message": "If the email is valid, a verification link was sent."}), 200
        uid = _generate_id()
        mock_db["users"][uid] = {
            "email": email,
            "name": name or email.split("@")[0],
            "role": role,
            "password_hash": hashed,
            "email_verified": False,
            "created_at": _now_iso(),
        }
        mock_db.setdefault("verification_tokens", {})[verification_token] = {
            "user_id": uid,
            "created_at": _now_iso(),
        }
        _save_mock_db()

    print(f"\\n[EMAIL MOCK] To: {email} \\nVerify your email: http://localhost:5173/#/verify-email?token={verification_token}\\n")
    return jsonify({"message": "If the email is valid, a verification link was sent."}), 201


@app.route("/api/auth/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Token missing"}), 400

    if FIREBASE_MODE:
        doc_ref = db.collection("verification_tokens").document(token)
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "Invalid or expired token"}), 400
        user_id = doc.to_dict()["user_id"]
        db.collection("users").document(user_id).update({"email_verified": True})
        doc_ref.delete()
    else:
        vtokens = mock_db.get("verification_tokens", {})
        if token not in vtokens:
            return jsonify({"error": "Invalid or expired token"}), 400
        user_id = vtokens[token]["user_id"]
        mock_db["users"][user_id]["email_verified"] = True
        del vtokens[token]
        _save_mock_db()
        
    return jsonify({"message": "Email successfully verified!"}), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT inside an HttpOnly cookie."""
    ip = request.remote_addr
    if not rate_limit(f"log_{ip}", limit=5, window=60):
        return jsonify({"error": "Too many login attempts. Try again later."}), 429

    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Invalid email or password"}), 401

    user = None
    uid = None

    if FIREBASE_MODE:
        existing = _fs_get_collection("users", filters=[("email", "==", email)], limit=1)
        if existing:
            user = existing[0]
            uid = user["id"]
    else:
        for u_id, u in mock_db["users"].items():
            if u["email"] == email:
                user = u
                uid = u_id
                break

    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"error": "Invalid email or password"}), 401
        
    if not user.get("email_verified", True):
        return jsonify({"error": "Please verify your email address first."}), 403

    identity = {"uid": uid, "email": email, "name": user.get("name", ""), "role": user.get("role", "farmer")}
    token = create_access_token(identity=identity)
    
    response = jsonify({"message": "Login successful", "user": identity})
    set_access_cookies(response, token)
    return response, 200


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@app.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"message": "If that email is in our database, we will send a password reset link."}), 200

    reset_token = _generate_id() + _generate_id()

    if FIREBASE_MODE:
        existing = _fs_get_collection("users", filters=[("email", "==", email)], limit=1)
        if existing:
            user_id = existing[0]["id"]
            db.collection("password_reset_tokens").document(reset_token).set({
                "user_id": user_id,
                "created_at": firestore.SERVER_TIMESTAMP,
            })
    else:
        user_id = None
        for u_id, u in mock_db["users"].items():
            if u["email"] == email:
                user_id = u_id
                break
        if user_id:
            mock_db.setdefault("password_reset_tokens", {})[reset_token] = {
                "user_id": user_id,
                "created_at": _now_iso(),
            }
            _save_mock_db()

    print(f"\\n[EMAIL MOCK] To: {email} \\nReset your password: http://localhost:5173/#/reset-password?token={reset_token}\\n")
    return jsonify({"message": "If that email is in our database, we will send a password reset link."}), 200


@app.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    new_password = data.get("password", "")
    
    if not token or len(new_password) < 12:
        return jsonify({"error": "Invalid token or password too short (min 12)"}), 400

    hashed = generate_password_hash(new_password)

    if FIREBASE_MODE:
        doc_ref = db.collection("password_reset_tokens").document(token)
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "Invalid or expired token"}), 400
        user_id = doc.to_dict()["user_id"]
        db.collection("users").document(user_id).update({"password_hash": hashed})
        doc_ref.delete()
    else:
        rtokens = mock_db.get("password_reset_tokens", {})
        if token not in rtokens:
            return jsonify({"error": "Invalid or expired token"}), 400
        user_id = rtokens[token]["user_id"]
        mock_db["users"][user_id]["password_hash"] = hashed
        del rtokens[token]
        _save_mock_db()
        
    return jsonify({"message": "Password successfully reset!"}), 200


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def auth_me():
    """Return current authenticated user."""
    return jsonify({"user": get_jwt_identity()}), 200


'''

new_content = content[:auth_start] + new_auth + content[auth_end:]

# Add set_access_cookies and unset_jwt_cookies to imports
if 'set_access_cookies' not in new_content:
    new_content = new_content.replace('from flask_jwt_extended import (', 'from flask_jwt_extended import (\\n    set_access_cookies,\\n    unset_jwt_cookies,')

# Configure JWT to use cookies
jwt_config = '''
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "smart-irrigation-jwt-secret-2024")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=24)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # True in prod with HTTPS
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False 
jwt = JWTManager(app)
'''

import re
new_content = re.sub(r'app\.config\["JWT_SECRET_KEY"\].*?jwt = JWTManager\(app\)', jwt_config.strip(), new_content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Updated app.py')
