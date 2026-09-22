import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_community_flow():
    print("--- Testing Community Backend Integration ---")
    
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

    # 2. GET /community/posts
    posts_resp = requests.get(f"{BASE_URL}/community/posts", headers=headers)
    print(f"GET /community/posts: Status {posts_resp.status_code}")
    assert posts_resp.status_code == 200
    posts = posts_resp.json()
    print(f"  Retrieved {len(posts)} discussion posts.")

    # 3. POST /community/posts (Create post)
    new_post_payload = {
        "title": "Real-Time Verification: Student Technical Discussion",
        "content": "Testing real-time Module 11 Community workspace integration for technical post creation.",
        "post_type": "DISCUSSION",
        "tags": ["react", "fastapi", "community"]
    }
    create_post_resp = requests.post(f"{BASE_URL}/community/posts", headers=headers, json=new_post_payload)
    print(f"POST /community/posts: Status {create_post_resp.status_code}")
    assert create_post_resp.status_code == 201
    created_post = create_post_resp.json()
    print(f"  Created Post ID: {created_post['id']} - Title: {created_post['title']}")

    # 4. POST /community/posts/{post_id}/comments (Create comment)
    post_id = created_post['id']
    comment_payload = {
        "content": "This is a real-time verification comment on the technical post."
    }
    comment_resp = requests.post(f"{BASE_URL}/community/posts/{post_id}/comments", headers=headers, json=comment_payload)
    print(f"POST /community/posts/{post_id}/comments: Status {comment_resp.status_code}")
    assert comment_resp.status_code == 201
    created_comment = comment_resp.json()
    print(f"  Created Comment ID: {created_comment['id']}")

    # 5. GET /community/peer-skills
    peer_skills_resp = requests.get(f"{BASE_URL}/community/peer-skills", headers=headers)
    print(f"GET /community/peer-skills: Status {peer_skills_resp.status_code}")
    assert peer_skills_resp.status_code == 200
    peer_skills = peer_skills_resp.json()
    print(f"  Retrieved {len(peer_skills)} peer skill exchange requests.")

    # 6. GET /community/activities
    activities_resp = requests.get(f"{BASE_URL}/community/activities", headers=headers)
    print(f"GET /community/activities: Status {activities_resp.status_code}")
    assert activities_resp.status_code == 200
    activities = activities_resp.json()
    print(f"  Retrieved {len(activities)} campus activities.")

    print("\nALL COMMUNITY BACKEND CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_community_flow()
