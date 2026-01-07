import httpx
import time

BASE_URL = "http://localhost:8000"

def test_registration_flow():
    # randomized username to ensure it doesn't exist yet
    username = f"test_user_{int(time.time())}"
    password = "test_password"
    
    print(f"--- Attempt 1: Register New User '{username}' ---")
    try:
        response = httpx.post(
            f"{BASE_URL}/register", 
            json={"username": username, "password": password}
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print(f"\n--- Attempt 2: Register DUPLICATE User '{username}' ---")
    try:
        response = httpx.post(
            f"{BASE_URL}/register", 
            json={"username": username, "password": password}
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration_flow()
