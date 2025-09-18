#!/usr/bin/env python3
"""Enhanced T1M Story Status System"""

import os
import json
import sys
from datetime import datetime

def check_files():
    """Check if key files exist"""
    files = {
        'src/api/app.py': 'Flask API',
        'src/api/conversation_manager.py': 'Conversation System',
        'src/api/analysis/documentary_style_analyzer.py': 'Nichols Analyzer',
        'src/api/story_analyzer.py': 'McKee Structure',
        'docs/THEORETICAL_FRAMEWORK.md': 'Academic Theory',
        '.claude_context.json': 'Session Context',
        'PROJECT_STATUS.md': 'Project Status'
    }
    
    print("\n📁 FILE STATUS:")
    all_present = True
    for path, desc in files.items():
        if os.path.exists(path):
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} (missing: {path})")
            all_present = False
    return all_present

def show_context():
    """Display session context"""
    if os.path.exists('.claude_context.json'):
        with open('.claude_context.json', 'r') as f:
            context = json.load(f)
        print("\n🔧 SYSTEM CONFIGURATION:")
        print(f"  Version: {context.get('version', 'Unknown')}")
        print(f"  Test Deck: {context.get('test_deck', 'Not set')}")
        print("\n  Working Features:")
        for feature in context.get('working_features', []):
            print(f"    ✓ {feature}")
        print("\n  Not Implemented:")
        for feature in context.get('not_implemented', []):
            print(f"    ⏸ {feature}")

def show_commands():
    """Display useful commands"""
    print("\n🚀 COMMANDS:")
    print("\n  Start Flask:")
    print("    python src/api/app.py")
    print("\n  Test conversational questions:")
    print("    curl -X POST -H 'Content-Type: application/json' \\")
    print("      -d '{\"deck_id\":\"fc324380-84eb-4d70-a7ac-73f6e7db75e6\"}' \\")
    print("      http://localhost:5001/api/start-conversation")
    print("\n  Share with new Claude session:")
    print("    cat PROJECT_STATUS.md docs/THEORETICAL_FRAMEWORK.md .claude_context.json")

def main():
    print("\n" + "="*70)
    print(" T1M STORY STATUS CHECK - " + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("="*70)
    
    # Check files
    files_ok = check_files()
    
    # Show context
    show_context()
    
    # Show commands
    show_commands()
    
    # Summary
    print("\n" + "="*70)
    if files_ok:
        print(" ✅ SYSTEM READY - All core files present")
    else:
        print(" ⚠️  MISSING FILES - Check above for details")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
