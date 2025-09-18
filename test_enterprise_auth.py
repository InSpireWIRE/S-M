"""Test enterprise authentication"""
import requests
import json

base_url = "http://localhost:5001"

# Test company registration
print("Testing company registration...")
response = requests.post(f"{base_url}/api/register", json={
    "company_name": "Test Productions",
    "email": "admin@testprod.com",
    "password": "TestPass123"
})
print(f"Registration: {response.json()}")

# Test login
print("\nTesting login...")
response = requests.post(f"{base_url}/api/login", json={
    "email": "admin@testprod.com",
    "password": "TestPass123"
})
print(f"Login: {response.json()}")
