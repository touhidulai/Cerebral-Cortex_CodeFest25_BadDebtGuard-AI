"""
Quick test to verify OpenAI API key is working
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
        print("❌ OpenAI API key not configured in .env file")
        return False
    
    print(f"🔑 API Key found: {api_key[:20]}...")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Make a simple test call
        print("\n🧪 Testing OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for quick test
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello' if you can read this."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API is WORKING!")
        print(f"   Response: {result}")
        print(f"   Model: {response.model}")
        print(f"   Tokens used: {response.usage.total_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        error_str = str(e)
        
        if "invalid_api_key" in error_str or "Incorrect API key" in error_str:
            print("\n💡 The API key is invalid or expired.")
            print("   Please get a new key from: https://platform.openai.com/api-keys")
        elif "insufficient_quota" in error_str:
            print("\n💡 The API key has no remaining credits.")
            print("   Please add credits at: https://platform.openai.com/account/billing")
        elif "rate_limit" in error_str:
            print("\n💡 Rate limit exceeded. Wait a moment and try again.")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  OpenAI API Connection Test")
    print("=" * 60)
    
    success = test_openai_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ RESULT: OpenAI API key is valid and working!")
    else:
        print("❌ RESULT: OpenAI API key is NOT working!")
    print("=" * 60)
