#!/bin/bash
echo "Rebranding S!M to S!M (Story Intelligence Machine)"
echo "NOTE: T!M (main system) remains unchanged"

# Replace ONLY "S!M" and "TIM Story" references with S!M
find . -name "*.py" -exec sed -i 's/S!M/S!M/g' {} \;
find . -name "*.py" -exec sed -i 's/TIM Story/S!M/g' {} \;

# Replace in Markdown files
find . -name "*.md" -exec sed -i 's/S!M/S!M (Story Intelligence Machine)/g' {} \;
find . -name "*.md" -exec sed -i 's/S!M/S!M/g' {} \;

# Replace in shell scripts
find . -name "*.sh" -exec sed -i 's/S!M/S!M/g' {} \;
find . -name "*.sh" -exec sed -i 's/S!M/S!M/g' {} \;

# Fix the project tag in Python files
find . -name "*.py" -exec sed -i 's/"project": "TIM Story"/"project": "S!M"/g' {} \;

echo "Rebranding complete: S!M → S!M"
echo "T!M (main system) remains unchanged"
