"""
Quick test to verify LLMOps API can start
"""

from backend.app.llmops_api import app
from fastapi.testclient import TestClient

# Create test client
client = TestClient(app)

print("=" * 70)
print("LLMOps API Quick Verification")
print("=" * 70)

# Test root endpoint
print("\nTesting root endpoint...")
response = client.get("/")
assert response.status_code == 200
print(f"✓ Root endpoint working: {response.json()['message']}")

# Test health endpoint
print("\nTesting health endpoint...")
response = client.get("/health")
assert response.status_code == 200
health = response.json()
print(f"✓ Health check passed")
print(f"  Provider: {health['provider']}")
print(f"  Model: {health['model']}")

# Test config endpoint
print("\nTesting config endpoint...")
response = client.get("/config")
assert response.status_code == 200
config = response.json()
print(f"✓ Config endpoint working")
print(f"  Use Groq: {config['use_groq']}")
print(f"  Temperature: {config['temperature']}")

# Test providers endpoint
print("\nTesting providers endpoint...")
response = client.get("/providers")
assert response.status_code == 200
providers = response.json()
print(f"✓ Providers endpoint working")
print(f"  Current Provider: {providers['current_provider']}")

print("\n" + "=" * 70)
print("✅ All API Endpoints Verified Successfully!")
print("=" * 70)
print("\nTo start the server, run:")
print("  python llmops_api.py")
print("\nOr use the batch file:")
print("  start_llmops_api.bat")
print("\nThen access the API at:")
print("  http://localhost:8000/docs")
print("=" * 70)
