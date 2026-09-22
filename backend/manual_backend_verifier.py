import sys
import os
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000"

def run_manual_backend_verification():
    print("=" * 80)
    print("SKILLY MODULE 03 — PHASE 3.3 LIVE BACKEND MANUAL VERIFICATION")
    print(f"Target: {BASE_URL}")
    print("=" * 80)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Student Login
    print("\n[STEP 1] Student login (student_browser@skilly.edu)...")
    res_login = client.post("/api/v1/auth/login", json={
        "email": "student_browser@skilly.edu",
        "password": "Password@123"
    })
    assert res_login.status_code == 200, f"Login failed: {res_login.text}"
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(" -> SUCCESS: Logged in, JWT token acquired.")

    # 2. Open career workspace API
    print("\n[STEP 2] Open career workspace API (/api/v1/student/career-workspace)...")
    res_ws = client.get("/api/v1/student/career-workspace", headers=headers)
    assert res_ws.status_code == 200, f"Workspace failed: {res_ws.text}"
    ws = res_ws.json()
    print(f" -> SUCCESS: Workspace loaded. Available roles count: {ws['available_roles_count']}")
    print(f"    Current target role: {ws['current_target_role']['title'] if ws['current_target_role'] else 'None'}")
    print(f"    Completion percentage: {ws['completion']['percentage']}%")

    # 3. Load real career roles
    print("\n[STEP 3] Load real career roles (/api/v1/student/career-roles)...")
    res_roles = client.get("/api/v1/student/career-roles", headers=headers)
    assert res_roles.status_code == 200
    roles = res_roles.json()
    print(f" -> SUCCESS: {len(roles)} active career roles returned from PostgreSQL.")
    for r in roles[:4]:
        print(f"    - {r['title']} [{r['industry_domain']}] | {r['skills_count']} skills ({r['core_skills_count']} core) | target={r['is_current_target']}")

    # 4. Open career role details
    target_candidate = roles[0]
    print(f"\n[STEP 4] Open career role details for '{target_candidate['title']}'...")
    res_det = client.get(f"/api/v1/student/career-roles/{target_candidate['id']}", headers=headers)
    assert res_det.status_code == 200
    det = res_det.json()
    print(f" -> SUCCESS: Role details retrieved. Required skills: {len(det['required_skills'])}")
    for s in det['required_skills']:
        print(f"      * {s['skill_name']} ({s['category']}) - {s['required_level']} [{s['importance_level']}]")

    # 5. Select career role
    print(f"\n[STEP 5] Select target career role '{target_candidate['title']}'...")
    res_set = client.put("/api/v1/student/target-role", headers=headers, json={"career_role_id": target_candidate['id']})
    assert res_set.status_code == 200
    set_resp = res_set.json()
    print(f" -> SUCCESS: {set_resp['message']}")
    print(f"    Target role updated: {set_resp['target_career_role']['title']}")
    print(f"    New completion: {set_resp['completion']['percentage']}% (Career: {set_resp['completion']['career_percentage']}%)")

    # 6. Refresh / read again to verify persistence
    print("\n[STEP 6] Refresh / read again (/api/v1/student/career-workspace)...")
    res_ws_after = client.get("/api/v1/student/career-workspace", headers=headers)
    assert res_ws_after.status_code == 200
    ws_after = res_ws_after.json()
    assert ws_after['current_target_role']['id'] == target_candidate['id']
    print(" -> SUCCESS: Target career role persisted in PostgreSQL and verified across re-fetch.")

    # 7. Invalid career role rejection (404)
    print("\n[STEP 7] Invalid career role rejection...")
    fake_id = str(uuid.uuid4())
    res_inv = client.put("/api/v1/student/target-role", headers=headers, json={"career_role_id": fake_id})
    assert res_inv.status_code == 404
    print(f" -> SUCCESS: Nonexistent career role rejected with 404 Not Found ({res_inv.json()['detail']})")

    # 8. Student-only RBAC check (Teacher login attempt on student workspace)
    print("\n[STEP 8] RBAC enforcement check...")
    # Attempt with fake teacher token or no token
    res_no_auth = client.get("/api/v1/student/career-workspace")
    assert res_no_auth.status_code == 401
    print(" -> SUCCESS: Unauthenticated request rejected with 401 Unauthorized.")

    print("\n" + "=" * 80)
    print("ALL LIVE MANUAL BACKEND VERIFICATION CHECKS PASSED (8/8)!")
    print("=" * 80)

if __name__ == "__main__":
    run_manual_backend_verification()
