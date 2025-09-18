#!/usr/bin/env python3
"""T1M Story Project Status Reporter"""

import os
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.development')

def main():
    print("\n" + "="*60)
    print("T1M STORY PROJECT STATUS")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Check key files
    print("\n📁 KEY FILES:")
    files = [
        'src/api/app.py',
        'src/api/conversation_manager.py',
        'src/api/analysis/documentary_style_analyzer.py',
        'docs/THEORETICAL_FRAMEWORK.md'
    ]
    for f in files:
        status = "✓" if os.path.exists(f) else "✗"
        print(f"  {status} {f}")
    
    print("\n🧪 TEST COMMANDS:")
    print("  python src/api/app.py")
    print('  curl -X POST -H "Content-Type: application/json" \\')
    print('    -d \'{"deck_id":"fc324380-84eb-4d70-a7ac-73f6e7db75e6"}\' \\')
    print('    http://localhost:5001/api/start-conversation')
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
