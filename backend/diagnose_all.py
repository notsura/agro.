from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.agroassist

print("=== USERS COLLECTION ===")
users = list(db.users.find())
user_map = {}
for u in users:
    uid = str(u['_id'])
    user_map[uid] = u.get('fullname', 'N/A')
    print(f"User: {u.get('fullname')} | ID: {uid} | Email: {u.get('email')}")

print("\n=== USER_CROPS COLLECTION ===")
user_crops = list(db.user_crops.find())
for uc in user_crops:
    uid = uc.get('user_id')
    owner = user_map.get(uid, "UNKNOWN USER")
    print(f"Crop: {uc.get('crop_name')} | UserID: {uid} (Type: {type(uid).__name__}) | Owner: {owner}")
    print(f"  Sowing: {uc.get('sowing_date')} | Started: {uc.get('started_at')}")

print("\n=== CROPS COLLECTION (Routines) ===")
crops = list(db.crops.find())
for c in crops:
    print(f"Crop Available: {c.get('name')}")

print("\n=== DIAGNOSTICS ===")
if not user_crops:
    print("CRITICAL: No documents in user_crops!")
else:
    for uc in user_crops:
        crop_name = uc.get('crop_name')
        matching_crop = db.crops.find_one({"name": {"$regex": f"^{crop_name}$", "$options": "i"}})
        if not matching_crop:
            print(f"WARNING: Journey for '{crop_name}' has NO matching routine in crops collection!")
        else:
            print(f"OK: Journey for '{crop_name}' has valid routine.")
