#!/bin/bash
# T1M Story Complete Session Initializer

echo "======================================"
echo " T1M STORY - SESSION INITIALIZATION"
echo "======================================"
echo ""

# Update the date in PROJECT_STATUS.md
TODAY=$(date +%Y-%m-%d)
sed -i "s/Last Updated:.*/Last Updated: $TODAY/" PROJECT_STATUS.md 2>/dev/null

# Run the comprehensive status check
python3 status_check.py

# Create a session summary for sharing
cat > session_summary.txt << EOL
T1M STORY SESSION SUMMARY - $(date)
=====================================

PROJECT: Documentary pitch development platform
VERSION: 0.2.0
STATUS: Conversational questions working

WHAT IT DOES:
- Analyzes documentary pitches
- Detects narrative gaps (McKee)
- Identifies documentary style (Nichols)
- Asks conversational coaching questions

RECENT SESSION WORK:
- Implemented database-driven questions
- Fixed universal gap detection
- Created documentation system

TEST WITH:
Deck ID: fc324380-84eb-4d70-a7ac-73f6e7db75e6

TO START WORKING:
1. python src/api/app.py (terminal 1)
2. Test with curl command (terminal 2)
EOL

echo "📄 Session summary created: session_summary.txt"
echo ""
echo "TO START WORKING:"
echo "  1. python src/api/app.py"
echo "  2. Use test commands from status output"
echo ""
echo "TO SHARE WITH NEW SESSION:"
echo "  cat session_summary.txt"
echo ""
