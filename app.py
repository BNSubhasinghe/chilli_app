from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "chilli_rover_r26_it_075_secret"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["chilli"]
users_col = db["users"]
sensor_logs_col = db["sensor_logs"]
disease_logs_col = db["disease_logs"]
field_zones_col = db["field_zones"]
soil_health_col = db["soil_health"]

# ── seed a default admin if none exists ──────────────────────────────────────
if users_col.count_documents({}) == 0:
    users_col.insert_one({
        "username": "admin",
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "full_name": "System Administrator",
        "created_at": datetime.utcnow()
    })
# Bhagaya's commit
# ── seed some demo records if empty ─────────────────────────────────────────
if sensor_logs_col.count_documents({}) == 0:
    sensor_logs_col.insert_many([
        {"date": "2025-03-01", "VW_30cm": 0.31, "VW_60cm": 0.27, "T_30cm": 24.1, "anomaly": 0, "recorded_at": datetime.utcnow()},
        {"date": "2025-03-02", "VW_30cm": 0.78, "VW_60cm": 0.12, "T_30cm": 31.5, "anomaly": 1, "recorded_at": datetime.utcnow()},
        {"date": "2025-03-03", "VW_30cm": 0.34, "VW_60cm": 0.29, "T_30cm": 23.8, "anomaly": 0, "recorded_at": datetime.utcnow()},
    ])

if disease_logs_col.count_documents({}) == 0:
    disease_logs_col.insert_many([
        {"image_name": "leaf_001.jpg", "prediction": "Healthy", "confidence": 0.96, "recorded_at": datetime.utcnow()},
        {"image_name": "leaf_002.jpg", "prediction": "Leaf Curl", "confidence": 0.88, "recorded_at": datetime.utcnow()},
        {"image_name": "leaf_003.jpg", "prediction": "Powdery Mildew", "confidence": 0.79, "recorded_at": datetime.utcnow()},
    ])

if field_zones_col.count_documents({}) == 0:
    field_zones_col.insert_many([
        {"zone": "Zone A", "cluster": 0, "ndvi": 0.72, "ndwi": 0.41, "area_pct": 34, "label": "High Vegetation", "recorded_at": datetime.utcnow()},
        {"zone": "Zone B", "cluster": 1, "ndvi": 0.45, "ndwi": 0.22, "area_pct": 28, "label": "Moderate Vegetation", "recorded_at": datetime.utcnow()},
        {"zone": "Zone C", "cluster": 2, "ndvi": 0.18, "ndwi": 0.08, "area_pct": 22, "label": "Sparse / Bare Soil", "recorded_at": datetime.utcnow()},
        {"zone": "Zone D", "cluster": 3, "ndvi": 0.61, "ndwi": 0.55, "area_pct": 16, "label": "Water / Wet Area", "recorded_at": datetime.utcnow()},
    ])

if soil_health_col.count_documents({}) == 0:
    soil_health_col.insert_many([
        {"nitrogen": 82, "phosphorus": 54, "potassium": 48, "ph": 6.4, "humidity": 71, "prediction": "Healthy", "model": "XGBoost", "recorded_at": datetime.utcnow()},
        {"nitrogen": 34, "phosphorus": 21, "potassium": 19, "ph": 5.1, "humidity": 42, "prediction": "Poor", "model": "LSTM", "recorded_at": datetime.utcnow()},
        {"nitrogen": 58, "phosphorus": 40, "potassium": 37, "ph": 6.8, "humidity": 61, "prediction": "Moderate", "model": "XGBoost", "recorded_at": datetime.utcnow()},
    ])


# ── auth decorator ───────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = users_col.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["full_name"] = user.get("full_name", username)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Summary counts for cards
    total_sensor_logs = sensor_logs_col.count_documents({})
    anomaly_count = sensor_logs_col.count_documents({"anomaly": 1})
    disease_count = disease_logs_col.count_documents({})
    disease_detected = disease_logs_col.count_documents({"prediction": {"$ne": "Healthy"}})
    zone_count = field_zones_col.count_documents({})
    soil_poor = soil_health_col.count_documents({"prediction": "Poor"})

    recent_anomalies = list(sensor_logs_col.find({"anomaly": 1}).sort("recorded_at", -1).limit(4))
    recent_diseases = list(disease_logs_col.find().sort("recorded_at", -1).limit(4))
    zones = list(field_zones_col.find().sort("zone", 1))
    recent_soil = list(soil_health_col.find().sort("recorded_at", -1).limit(4))

    return render_template("dashboard.html",
        user=session["user"],
        full_name=session["full_name"],
        total_sensor_logs=total_sensor_logs,
        anomaly_count=anomaly_count,
        disease_count=disease_count,
        disease_detected=disease_detected,
        zone_count=zone_count,
        soil_poor=soil_poor,
        recent_anomalies=recent_anomalies,
        recent_diseases=recent_diseases,
        zones=zones,
        recent_soil=recent_soil,
    )


# ── API endpoints for charts ─────────────────────────────────────────────────
@app.route("/api/anomaly_trend")
@login_required
def api_anomaly_trend():
    logs = list(sensor_logs_col.find({}, {"_id": 0, "date": 1, "VW_30cm": 1, "anomaly": 1}).sort("date", 1))
    return jsonify(logs)


@app.route("/api/soil_health_dist")
@login_required
def api_soil_health_dist():
    pipeline = [{"$group": {"_id": "$prediction", "count": {"$sum": 1}}}]
    result = {doc["_id"]: doc["count"] for doc in soil_health_col.aggregate(pipeline)}
    return jsonify(result)


@app.route("/api/zone_dist")
@login_required
def api_zone_dist():
    zones = list(field_zones_col.find({}, {"_id": 0, "zone": 1, "area_pct": 1, "label": 1}))
    return jsonify(zones)


@app.route("/api/disease_dist")
@login_required
def api_disease_dist():
    pipeline = [{"$group": {"_id": "$prediction", "count": {"$sum": 1}}}]
    result = {doc["_id"]: doc["count"] for doc in disease_logs_col.aggregate(pipeline)}
    return jsonify(result)


# ── users management (simple) ────────────────────────────────────────────────
@app.route("/users")
@login_required
def users():
    all_users = list(users_col.find({}, {"password": 0, "_id": 0}))
    return render_template("users.html", users=all_users,
                           user=session["user"], full_name=session["full_name"])


@app.route("/users/add", methods=["POST"])
@login_required
def add_user():
    uname = request.form.get("username", "").strip()
    pwd = request.form.get("password", "")
    fname = request.form.get("full_name", "").strip()
    if not uname or not pwd:
        flash("Username and password are required.", "error")
        return redirect(url_for("users"))
    if users_col.find_one({"username": uname}):
        flash("Username already exists.", "error")
        return redirect(url_for("users"))
    users_col.insert_one({
        "username": uname,
        "password": generate_password_hash(pwd),
        "role": "viewer",
        "full_name": fname or uname,
        "created_at": datetime.utcnow()
    })
    flash(f"User '{uname}' created successfully.", "success")
    return redirect(url_for("users"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
