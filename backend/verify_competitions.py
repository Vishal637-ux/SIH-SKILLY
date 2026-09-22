import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_competitions_flow():
    print("--- Testing Competitions & Activities Backend Integration ---")
    
    # 1. Login as student
    login_data = {
        "email": "student_browser@skilly.edu",
        "password": "Password@123"
    }
    
    auth_resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if auth_resp.status_code != 200:
        print(f"FAILED to login: {auth_resp.status_code} - {auth_resp.text}")
        return

    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login SUCCESSFUL")

    # 2. GET /community/activities
    activities_resp = requests.get(f"{BASE_URL}/community/activities", headers=headers)
    print(f"GET /community/activities: Status {activities_resp.status_code}")
    assert activities_resp.status_code == 200
    activities = activities_resp.json()
    print(f"  Retrieved {len(activities)} campus activities & competitions.")

    if len(activities) > 0:
        item = activities[0]
        print(f"  Sample Item Title: {item.get('title')}")
        print(f"  Activity Type: {item.get('activity_type')}")
        print(f"  Institution: {item.get('institution_name')}")

    print("\nALL COMPETITIONS BACKEND CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_competitions_flow()
