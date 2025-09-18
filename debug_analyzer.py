#!/usr/bin/env python
import sys
sys.path.append('src/api')

from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer

analyzer = DocumentaryStyleAnalyzer()

test_text = "This documentary will prove that climate change threatens humanity. Through extensive data analysis and expert testimony, we will demonstrate the urgent crisis."

# Check what patterns are loaded
print("PATTERNS LOADED:")
for style, patterns in analyzer.style_patterns.items():
    print(f"\n{style}:")
    for pattern_type, pattern_list in patterns.items():
        print(f"  {pattern_type}: {pattern_list[:3]}...")

# Run the analysis
result = analyzer.analyze_pitch(test_text)
print(f"\n\nRESULT AFTER FIX:")
print(f"Detected styles: {result.get('dominant_styles', [])}")
print(f"Style scores: {result.get('style_scores', {})}")
print(f"Gaps: {result.get('gaps', [])}")
print(f"Confidence: {result.get('analysis_confidence', 0)}")
