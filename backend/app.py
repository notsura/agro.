from flask import Flask, jsonify, request
import urllib.request
import json
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import timedelta
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
# Enable CORS with support for credentials if needed, though simple setup is fine here.
CORS(app)
bcrypt = Bcrypt(app)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-agro-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# MongoDB Configuration
MONGO_URI = "mongodb+srv://agro:agro123@cluster0.artzmzx.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.agroassist

# --- Helper to serialize MongoDB docs ---
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# --- RBAC Decorator ---
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"message": "Administrator access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- Auth Routes ---

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    fullname = data.get('fullname')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
        
    if db.users.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user_data = {
        "email": email,
        "password": hashed_password,
        "fullname": fullname,
        "role": "farmer"
    }
    
    db.users.insert_one(user_data)
    return jsonify({"message": "User created successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = db.users.find_one({"email": email})
    
    if user and bcrypt.check_password_hash(user['password'], password):
        role = user.get('role', 'farmer')
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={"role": role}
        )
        return jsonify({
            "token": access_token,
            "user": {
                "id": str(user['_id']),
                "email": user['email'],
                "fullname": user.get('fullname'),
                "role": role
            }
        }), 200
        
    return jsonify({"message": "Invalid email or password"}), 401

# --- Existing Routes ---

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ping')
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_crop():
    data = request.json
    raw_soil = data.get('soil', '')
    raw_season = data.get('season', '')
    raw_water = data.get('water', '') # This is now 'Climate or Rainfall Condition'
    target_crop = data.get('crop', '').strip()
    preferred_category = data.get('category', 'All') # Grain, Fruit, Vegetable, Commercial, or All
    
    # Robust normalization
    soil = raw_soil.split(' ')[0] if raw_soil else 'Alluvial'
    season = raw_season.split(' ')[0] if raw_season else 'Kharif'
    
    # Climate normalization based on new labels
    climate = "Moderate"
    if "High" in raw_water:
        climate = "Hot"
    elif "Arid" in raw_water:
        climate = "Hot"
    elif "Moderate" in raw_water:
        climate = "Moderate"

# Logic 1: Find recommended crops based on suitability mapping in DB
    suitability_match = db.suitability.find_one({
        "soil": soil,
        "season": season,
        "climate": climate
    })
    
    is_exact_match = True
    if not suitability_match:
         is_exact_match = False
         suitability_match = db.suitability.find_one({"season": season})
    
    recommended_names = suitability_match.get("crops", ["Rice", "Wheat", "Maize"]) if suitability_match else ["Rice", "Wheat", "Maize"]
    
    results = []
    
    def get_score(crop_name, is_recommended):
        if is_recommended and is_exact_match:
            return 95 + (int(str(ObjectId())[-1], 16) % 5) # 95-99% for top tier
        
        crop_doc = db.crops.find_one({"name": crop_name})
        if not crop_doc: return 50 # Unknown
        
        score = 0
        creq = crop_doc.get("growing_season", "").lower()
        sreq = crop_doc.get("soil_preference", "").lower()
        wreq = crop_doc.get("water_requirement", "").lower()
        
        # Season Match (33%)
        if season.lower() in creq or ("kharif" in creq and season == "Kharif"):
            score += 33
        elif "rabi" in creq and season == "Winter":
            score += 33
        elif "zaid" in creq and season == "Summer":
            score += 33
            
        # Soil Match (33%)
        if soil.lower() in sreq:
            score += 33
            
        # Climate Match (34%)
        if climate == "Hot" and ("high" in wreq or "very high" in wreq):
            score += 34
        elif climate == "Moderate" and "moderate" in wreq:
            score += 34
        elif climate == "Cool" and "low" in wreq:
            score += 34
        elif climate == "Hot" and "moderate" in wreq:
            score += 15 # Partial
            
        # Base floor for recommended crops
        if is_recommended:
            score = max(score, 82)
            
        return min(score, 100)

    # Step 1: Add recommended crops to results
    for crop_name in recommended_names:
        query = {"name": crop_name}
        if preferred_category != 'All':
            query["category"] = {"$regex": f"^{preferred_category}", "$options": "i"}

        crop_data = db.crops.find_one(query)
        if crop_data:
            score = get_score(crop_name, True)
            results.append({
                "name": crop_name,
                "category": crop_data.get("category"),
                "routine": crop_data.get("routine", []),
                "suitability_percent": score,
                "suitability": "High" if score > 80 else "Moderate",
                "is_recommended": True
            })

    # Step 2: If user suggested a crop, check if it's already in results
    if target_crop:
        is_already_present = any(r['name'].lower() == target_crop.lower() for r in results)
        
        if not is_already_present:
            crop_data = db.crops.find_one({"name": {"$regex": f"^{target_crop}$", "$options": "i"}})
            
            if crop_data:
                score = get_score(crop_data['name'], False)
                results.append({
                    "name": crop_data['name'],
                    "category": crop_data.get("category"),
                    "routine": crop_data.get("routine", []),
                    "suitability_percent": score,
                    "suitability": "High" if score > 80 else ("Moderate" if score > 50 else "Low"),
                    "is_recommended": False,
                    "warning": f"⚠️ Caution: {crop_data['name']} has a {score}% match for your parameters. Traditionally, it faces challenges in {soil} soil during {season}." if score < 80 else None
                })
            else:
                # Totally unknown crop
                results.append({
                    "name": target_crop,
                    "routine": [
                        {"period": "General", "title": "Standard Care", "desc": "Follow local agronomic practices for this variety."},
                        {"period": "Monitoring", "title": "Pest Watch", "desc": "Keep a close eye on unconventional varieties."},
                        {"period": "Harvest", "title": "Maturity", "desc": "Harvest based on local visual indicators."}
                    ],
                    "suitability_percent": 30,
                    "suitability": "Unknown",
                    "is_recommended": False,
                    "warning": f"🚩 Custom Advisory: No historical data for '{target_crop}'. Proceed with calculated risk."
                })

    return jsonify(results)

@app.route('/api/crops', methods=['GET'])
def get_all_crops():
    crops = list(db.crops.find())
    return jsonify([serialize_doc(c) for c in crops])

# --- Admin API Endpoints ---

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    stats = {
        "users": db.users.count_documents({}),
        "crops": db.crops.count_documents({}),
        "posts": db.posts.count_documents({}),
        "market": db.market.count_documents({}),
        "active_journeys": db.user_crops.count_documents({})
    }
    return jsonify(stats)

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_admin_users():
    users = list(db.users.find({}, {"password": 0})) # Exclude passwords
    return jsonify([serialize_doc(u) for u in users])

@app.route('/api/admin/users/<user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    current_status = user.get("status", "active")
    new_status = "blocked" if current_status == "active" else "active"
    
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": new_status}})
    return jsonify({"status": new_status}), 200

@app.route('/api/admin/crops', methods=['POST'])
@admin_required
def add_crop():
    data = request.json
    result = db.crops.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return jsonify(data), 201

@app.route('/api/admin/crops/<crop_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_crop(crop_id):
    if request.method == 'PUT':
        data = request.json
        if "_id" in data: del data["_id"]
        db.crops.update_one({"_id": ObjectId(crop_id)}, {"$set": data})
        return jsonify({"message": "Crop updated"}), 200
    
    if request.method == 'DELETE':
        db.crops.delete_one({"_id": ObjectId(crop_id)})
        return jsonify({"message": "Crop deleted"}), 200

@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'GET':
        posts = list(db.posts.find().sort("_id", -1))
        return jsonify([serialize_doc(p) for p in posts])
    
    if request.method == 'POST':
        data = request.json
        new_post = {
            "author": data.get("author", "Anonymous"),
            "content": data.get("content"),
            "topic": data.get("topic", "General"),
            "image_url": data.get("image_url"), # Optional photo
            "timestamp": data.get("timestamp", "Just now"),
            "likes": [], # List of user IDs
            "comments": [], # List of comment objects
            "shares": 0
        }
        result = db.posts.insert_one(new_post)
        new_post["_id"] = str(result.inserted_id)
        return jsonify(new_post), 201

@app.route('/api/posts/<post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    user_id = get_jwt_identity()
    post = db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"message": "Post not found"}), 404
        
    likes = post.get("likes", [])
    if user_id in likes:
        likes.remove(user_id)
    else:
        likes.append(user_id)
        
    db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": {"likes": likes}})
    return jsonify({"likes": likes}), 200

@app.route('/api/posts/<post_id>/comment', methods=['POST'])
@jwt_required()
def comment_post(post_id):
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    data = request.json
    content = data.get("content")
    
    if not content:
        return jsonify({"message": "Comment content is required"}), 400
        
    comment = {
        "author": user.get("fullname", "Anonymous"),
        "content": content,
        "timestamp": "Just now"
    }
    
    db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )
    return jsonify(comment), 200

@app.route('/api/market', methods=['GET'])
def get_market():
    market_data = list(db.market.find())
    return jsonify([serialize_doc(m) for m in market_data])

@app.route('/api/resources', methods=['GET'])
def get_resources():
    resources = list(db.resources.find())
    return jsonify([serialize_doc(r) for r in resources])

# --- Day-by-Day Follow-up Routes ---

@app.route('/api/user/start-followup', methods=['POST'])
@jwt_required()
def start_followup():
    user_id = get_jwt_identity()
    data = request.json
    crop_name = data.get('crop_name')
    sowing_date = data.get('sowing_date') # ISO format string like "2026-02-03"
    
    if not crop_name or not sowing_date:
        return jsonify({"message": "Crop name and sowing date are required"}), 400
        
    # Find existing journey type-agnotically
    try:
        query = {"$or": [{"user_id": user_id}, {"user_id": ObjectId(user_id)}]}
    except:
        query = {"user_id": user_id}
    
    existing = db.user_crops.find_one(query)
    
    update_data = {
        "user_id": user_id, # Ensure it's stored as string
        "crop_name": crop_name,
        "sowing_date": sowing_date,
        "started_at": sowing_date,
        "completed_tasks": [] # Reset for new journey
    }

    if existing:
        db.user_crops.update_one({"_id": existing["_id"]}, {"$set": update_data})
    else:
        db.user_crops.insert_one(update_data)

    print(f"DEBUG: Journey updated in DB for {user_id} with crop {crop_name}")
    return jsonify({"message": f"Journey for {crop_name} started!"}), 200

@app.route('/api/user/active-status', methods=['GET'])
@jwt_required()
def get_active_status():
    user_id = get_jwt_identity()
    try:
        query = {"$or": [{"user_id": user_id}, {"user_id": ObjectId(user_id)}]}
    except:
        query = {"user_id": user_id}

    user_crop = db.user_crops.find_one(query)
    print(f"DEBUG: Fetching status for {user_id} - Found: {user_crop.get('crop_name') if user_crop else 'None'}")
    
    if not user_crop:
        return jsonify({"active": False, "debug_user_id": user_id}), 200
        
    from datetime import datetime
    sowing_date = datetime.fromisoformat(user_crop['sowing_date'])
    today = datetime.now()
    days_since_sowing = (today - sowing_date).days + 1 # Day 1 is the sowing day
    
    # Case-insensitive lookup for routine
    crop_data = db.crops.find_one({"name": {"$regex": f"^{user_crop['crop_name']}$", "$options": "i"}})
    if not crop_data:
        return jsonify({"active": True, "error": "Crop data not found"}), 404
        
    current_task = None
    routine = crop_data.get('routine', [])
    for step in routine:
        if step['start_day'] <= days_since_sowing <= step['end_day']:
            current_task = step
            break
            
    # Also find next task
    next_task = None
    for step in routine:
        if step['start_day'] > days_since_sowing:
            next_task = step
            break
            
    return jsonify({
        "active": True,
        "crop_name": user_crop['crop_name'],
        "days_since_sowing": days_since_sowing,
        "current_task": current_task,
        "next_task": next_task,
        "routine": routine,
        "post_harvest": crop_data.get("post_harvest"), # Include post-harvest intelligence
        "completed_tasks": user_crop.get("completed_tasks", []), # List of task titles or IDs
        "debug_user_id": user_id
    })

@app.route('/api/user/complete-journey', methods=['POST'])
@jwt_required()
def complete_journey():
    user_id = get_jwt_identity()
    try:
        query = {"$or": [{"user_id": user_id}, {"user_id": ObjectId(user_id)}]}
    except:
        query = {"user_id": user_id}

    user_crop = db.user_crops.find_one(query)
    if not user_crop:
        return jsonify({"message": "No active journey to complete"}), 404

    # Archive to history
    from datetime import datetime
    sowing_date = datetime.fromisoformat(user_crop['sowing_date'])
    today = datetime.now()
    days_since_sowing = (today - sowing_date).days + 1

    history_entry = {
        "user_id": user_id,
        "crop_name": user_crop['crop_name'],
        "start_date": user_crop['sowing_date'],
        "completion_date": today.isoformat(),
        "duration": days_since_sowing,
        "status": "Harvested"
    }
    
    db.farming_history.insert_one(history_entry)
    db.user_crops.delete_one({"_id": user_crop["_id"]})
    
    return jsonify({"message": "Journey archived successfully!", "history": serialize_doc(history_entry)}), 200

@app.route('/api/user/history', methods=['GET'])
@jwt_required()
def get_farming_history():
    user_id = get_jwt_identity()
    history = list(db.farming_history.find({"user_id": user_id}).sort("completion_date", -1))
    return jsonify([serialize_doc(h) for h in history])

@app.route('/api/user/toggle-task', methods=['POST'])
@jwt_required()
def toggle_task():
    user_id = get_jwt_identity()
    data = request.json
    task_title = data.get('task_title')
    
    if not task_title:
        return jsonify({"message": "Task title is required"}), 400
        
    try:
        query = {"$or": [{"user_id": user_id}, {"user_id": ObjectId(user_id)}]}
    except:
        query = {"user_id": user_id}

    user_crop = db.user_crops.find_one(query)
    if not user_crop:
        return jsonify({"message": "No active journey"}), 404
        
    completed = user_crop.get("completed_tasks", [])
    if task_title in completed:
        completed.remove(task_title)
    else:
        completed.append(task_title)
        
    db.user_crops.update_one(
        {"user_id": user_id},
        {"$set": {"completed_tasks": completed}}
    )
    return jsonify({"completed_tasks": completed}), 200

@app.route('/api/weather', methods=['GET'])
def get_weather():
    # Coordinates for Saharanpur, UP (Agricultural hub)
    lat, lon = 29.968, 77.545
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            cw = data.get("current_weather", {})
            daily = data.get("daily", {})
            
            # Simple WMO Code mapping
            def map_weather(code):
                mapping = {
                    0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                    45: "Foggy", 48: "Rime Fog", 51: "Light Drizzle", 61: "Slight Rain",
                    63: "Moderate Rain", 65: "Heavy Rain", 95: "Thunderstorm"
                }
                return mapping.get(code, "Clear Sky")

            weather_response = {
                "location": "Saharanpur",
                "current": {
                    "temp": f"{int(cw.get('temperature', 24))}°",
                    "condition": map_weather(cw.get('weathercode', 0)),
                    "wind": f"{int(cw.get('windspeed', 12))} km/h",
                    "last_updated": "Just now"
                },
                "forecast": []
            }

            # Map 5-day forecast
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            from datetime import datetime
            
            for i in range(5):
                date_str = daily.get("time", [])[i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = days[date_obj.weekday()]
                
                weather_response["forecast"].append({
                    "day": day_name,
                    "temp": f"{int(daily.get('temperature_2m_max', [])[i])}°",
                    "condition": map_weather(daily.get('weathercode', [])[i])
                })

            return jsonify(weather_response)
    except Exception as e:
        print(f"Weather Fetch Error: {e}")
        return jsonify({"error": "Weather data unavailable"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

