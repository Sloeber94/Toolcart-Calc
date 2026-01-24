from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

# Get API credentials
API_KEY = os.getenv("ABBY_API_KEY")
APP_ID = os.getenv("ABBY_APPLICATION_ID")
API_BASE = os.getenv("ABBY_API_BASE")

# Verify variables loaded
print("🔍 Checking environment variables...")
print(f"✅ API Key loaded: {API_KEY[:15]}..." if API_KEY else "❌ API Key NOT found")
print(f"✅ App ID loaded: {APP_ID}" if APP_ID else "❌ App ID NOT found")
print(f"✅ API Base: {API_BASE}" if API_BASE else "❌ API Base NOT found")
print()

# Check if all required variables are set
if not API_KEY or not APP_ID:
    print("❌ ERROR: Missing required environment variables!")
    print("📝 Make sure your .env file contains:")
    print("   ABBY_API_KEY=your-key")
    print("   ABBY_APPLICATION_ID=your-app-id")
    exit(1)

# Test API connection
print("🚀 Testing Abby API connection...")
try:
    headers = {
        "X-ABBY-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "application_id": APP_ID,
        "query": "Hello, can you respond with a simple greeting?"
    }
    
    response = requests.post(
        f"{API_BASE}/agent_chat",
        headers=headers,
        json=payload,
        timeout=10
    )
    
    print(f"📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! API connection working!")
        print(f"📨 Response: {response.json()}")
    else:
        print(f"⚠️ Unexpected status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("💡 Check your network connection and API credentials")
