import requests
import time

BASE_URL = "http://localhost:5000/api"

def test_journey_sync():
    print("--- Starting Journey Sync Test ---")
    
    # 1. Signup/Login
    email = "test_farmer_v2@example.com"
    password = "password123"
    fullname = "Test Farmer V2"
    
    # Signup (might fail if exists, ignore)
    requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password, "fullname": fullname})
    
    # Login
    print(f"Logging in as {email}...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if login_resp.status_code != 200:
        print("Login failed!")
        return
    
    data = login_resp.json()
    token = data['token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"User ID from login: {data['user']['id']}")

    # 2. Check initial status
    print("\nChecking initial status...")
    status_resp = requests.get(f"{BASE_URL}/user/active-status", headers=headers)
    print(f"Initial Status: {status_resp.json()}")

    # 3. Start Journey (Maize)
    print("\nStarting journey for Maize...")
    start_resp = requests.post(f"{BASE_URL}/user/start-followup", 
                              json={"crop_name": "Maize", "sowing_date": "2026-02-03"}, 
                              headers=headers)
    print(f"Start Response: {start_resp.json()}")

    # 4. Check status immediately
    print("\nChecking status after start...")
    status_resp = requests.get(f"{BASE_URL}/user/active-status", headers=headers)
    print(f"Status After Start: {status_resp.json()}")

    # 5. Overwrite Journey (Tomato)
    print("\nOverwriting journey with Tomato...")
    start_resp = requests.post(f"{BASE_URL}/user/start-followup", 
                              json={"crop_name": "Tomato", "sowing_date": "2026-02-03"}, 
                              headers=headers)
    print(f"Overwrite Response: {start_resp.json()}")

    # 6. Check final status
    print("\nChecking final status...")
    status_resp = requests.get(f"{BASE_URL}/user/active-status", headers=headers)
    final_status = status_resp.json()
    print(f"Final Status: {final_status}")
    
    if final_status.get('active') and final_status.get('crop_name') == "Tomato":
        print("\n✅ SUCCESS: Journey updated correctly in backend.")
    else:
        print("\n❌ FAILURE: Journey did not update as expected.")

if __name__ == "__main__":
    test_journey_sync()
