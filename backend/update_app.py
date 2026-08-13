import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace register
register_pattern = re.compile(r'@app\.route\("/api/auth/register", methods=\["POST"\]\).*?def register\(\):.*?return response, 201', re.DOTALL)

new_register = '''@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").lower().strip()
    name = data.get("name", "")
    role = data.get("role", "farmer")
    
    uid = str(uuid.uuid4())
    hashed = generate_password_hash("dummy")
    
    user_data = {
        "email": email,
        "name": name or email.split("@")[0],
        "role": role,
        "password_hash": hashed,
        "email_verified": True,
        "created_at": _now_iso(),
    }
    
    if FIREBASE_MODE:
        db.collection("users").document(uid).set(user_data)
    else:
        mock_db["users"][uid] = user_data
        
    user_info = {"uid": uid, "email": email, "name": user_data["name"], "role": role}
    token = create_access_token(identity=user_info)
    response = jsonify({"message": "Registration successful", "user": user_info})
    set_access_cookies(response, token)
    return response, 201'''

content = register_pattern.sub(new_register, content)

# Replace login
login_pattern = re.compile(r'@app\.route\("/api/auth/login", methods=\["POST"\]\).*?def login\(\):.*?return response, 200', re.DOTALL)

new_login = '''@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").lower().strip()
    
    user = None
    uid = None
    
    if FIREBASE_MODE:
        users_ref = db.collection("users").where(filter=firestore.FieldFilter("email", "==", email)).limit(1).get()
        if users_ref:
            doc = users_ref[0]
            user = doc.to_dict()
            uid = doc.id
    else:
        for u_id, u in mock_db["users"].items():
            if u["email"] == email:
                user = u
                uid = u_id
                break
                
    if not user:
        # Auto register on the fly
        uid = str(uuid.uuid4())
        user = {
            "email": email,
            "name": email.split("@")[0],
            "role": "farmer",
            "password_hash": generate_password_hash("dummy"),
            "email_verified": True,
            "created_at": _now_iso(),
        }
        if FIREBASE_MODE:
            db.collection("users").document(uid).set(user)
        else:
            mock_db["users"][uid] = user

    user_info = {"uid": uid, "email": user["email"], "name": user.get("name", ""), "role": user.get("role", "farmer")}
    token = create_access_token(identity=user_info)
    response = jsonify({"message": "Login successful", "user": user_info})
    set_access_cookies(response, token)
    return response, 200'''

content = login_pattern.sub(new_login, content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Backend updated.")
