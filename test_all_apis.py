import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_apis():
    print("Testing APIs...")
    
    # 1. Registering user
    print("\n1. Testing User Registration (/auth/register)...")
    email = f"test_{int(time.time())}@example.com"
    pwd = "securepassword123"
    res_register = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": pwd})
    print(f"Status: {res_register.status_code}")
    print(f"Response: {res_register.text}")
    if res_register.status_code not in [200, 400]:
        print("[FAIL] Registration failed.")
        sys.exit(1)

    # 2. Log in
    print("\n2. Testing User Login (/auth/login)...")
    res_login = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": pwd})
    print(f"Status: {res_login.status_code}")
    print(f"Response: {res_login.text}")
    if res_login.status_code != 200:
        print("[FAIL] Login failed.")
        sys.exit(1)
        
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Generate Infographic
    print("\n3. Testing Infographic Generation (/infographics/generate)...")
    res_gen = requests.post(f"{BASE_URL}/infographics/generate", json={"topic": "Quantum Computing"}, headers=headers)
    print(f"Status: {res_gen.status_code}")
    print(f"Response: {res_gen.text}")
    if res_gen.status_code != 202:
        print("[FAIL] Generate requested failed.")
        sys.exit(1)
        
    job_id = res_gen.json()["id"]

    # 4. Check Status
    print(f"\n4. Testing Job Status (/infographics/status/{job_id})...")
    time.sleep(1) # wait briefly
    res_status = requests.get(f"{BASE_URL}/infographics/status/{job_id}", headers=headers)
    print(f"Status: {res_status.status_code}")
    print(f"Response: {res_status.text}")
    if res_status.status_code != 200:
        print("[FAIL] Status retrieval failed.")
        sys.exit(1)

    print("\n[SUCCESS] Basic core APIs responded successfully.")

if __name__ == "__main__":
    test_apis()
