#!/usr/bin/env python
import sys
sys.path.append('src/api')

from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer

analyzer = DocumentaryStyleAnalyzer()

# Test with argument-driven text
test_text = """
This documentary will prove that climate change threatens humanity. 
Through extensive data analysis and expert testimony, we will demonstrate 
the urgent crisis. Research from NASA clearly shows rising temperatures. 
Statistics reveal accelerating ice melt. We must convince policymakers to act.
"""

result = analyzer.analyze_pitch(test_text)

print("TEST RESULTS:")
print(f"Detected styles: {result.get('dominant_styles', [])}")
print(f"Style scores: {result.get('style_scores', {})}")
print(f"Gaps: {result.get('gaps', [])}")
print(f"Confidence: {result.get('analysis_confidence', 0)}")
