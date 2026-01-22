import os
from pathlib import Path

print("=" * 60)
print("DEBUG: Environment Variable Loader")
print("=" * 60)

# 1. Check current working directory
current_dir = os.getcwd()
print(f"\n📁 Current working directory:\n   {current_dir}")

# 2. Check if .env file exists
env_path = Path(".env")
env_exists = env_path.exists()
print(f"\n📄 .env file exists: {'✅ YES' if env_exists else '❌ NO'}")

if env_exists:
    print(f"   Location: {env_path.absolute()}")
    
    # 3. Read and display .env contents (first 50 chars of each line)
    print("\n📝 .env file contents:")
    try:
        with open('.env', 'r') as f:
            for i, line in enumerate(f.readlines(), 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Show only first 50 chars for security
                    display = line[:50] + "..." if len(line) > 50 else line
                    print(f"   Line {i}: {display}")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
else:
    print(f"   ❌ .env file not found in: {current_dir}")
    print("\n💡 TIP: Create .env file in the same folder as this script")

# 4. Try loading with python-dotenv
print("\n🔧 Attempting to load with python-dotenv...")
try:
    from dotenv import load_dotenv
    result = load_dotenv()
    print(f"   load_dotenv() returned: {result}")
    
    # 5. Check if variables are loaded
    print("\n🔍 Checking environment variables:")
    vars_to_check = ['ABBY_API_KEY', 'ABBY_APPLICATION_ID', 'ABBY_API_BASE']
    
    for var_name in vars_to_check:
        value = os.getenv(var_name)
        if value:
            # Show only first 20 chars
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"   ✅ {var_name}: {display_value}")
        else:
            print(f"   ❌ {var_name}: NOT FOUND")
            
except ImportError:
    print("   ❌ python-dotenv not installed!")
    print("   Run: pip install python-dotenv")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
