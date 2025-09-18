#!/bin/bash
# T1M Story Session Ender - Logs progress

echo "======================================"
echo " ENDING T1M STORY SESSION"
echo "======================================"

# Prompt for what was accomplished
echo ""
echo "What did you accomplish this session?"
read -r accomplishment

# Append to a progress log
echo "[$(date '+%Y-%m-%d %H:%M')] $accomplishment" >> PROGRESS_LOG.md

# If git is initialized, show what changed
if [ -d .git ]; then
    echo ""
    echo "📝 Files changed this session:"
    git status --short
    
    echo ""
    echo "Would you like to commit these changes? (y/n)"
    read -r commit_answer
    
    if [ "$commit_answer" = "y" ]; then
        git add -A
        git commit -m "Session update: $accomplishment"
        echo "✓ Changes committed"
    fi
fi

echo ""
echo "✓ Session ended and logged"
echo "See PROGRESS_LOG.md for history"
