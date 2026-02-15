from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.agroassist

print("--- Cleaning up user_crops duplicates ---")
# Strategy: Iterate through all users, if more than 1 journey exists, keep the latest one (highest _id)
user_ids = set()
for doc in db.user_crops.find():
    uid = doc.get('user_id')
    if uid:
        user_ids.add(uid)

for uid in user_ids:
    # Check for string or ObjectId versions
    query = {"$or": [{"user_id": uid}, {"user_id": ObjectId(uid) if len(uid) == 24 else None}]}
    journeys = list(db.user_crops.find(query).sort("_id", -1))
    
    if len(journeys) > 1:
        print(f"Found {len(journeys)} journeys for user {uid}. Keeping {journeys[0]['_id']}...")
        for j in journeys[1:]:
            db.user_crops.delete_one({"_id": j["_id"]})
            print(f"  Deleted duplicate {j['_id']}")

# Enforce Unique Index
try:
    db.user_crops.create_index("user_id", unique=True)
    print("Enforced unique index on user_id in user_crops.")
except Exception as e:
    print(f"Error creating unique index: {e}")

print("Cleanup complete.")
