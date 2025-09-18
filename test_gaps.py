import sys
sys.path.append('src/api')
from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer

analyzer = DocumentaryStyleAnalyzer()

# Test with text missing key elements
discovery_text = """
We will observe the daily routines of factory workers. 
Following their natural behavior without interference, 
we watch as their stories unfold organically. 
The process of change emerges gradually through patient observation.
"""

result = analyzer.analyze_pitch(discovery_text)
print("DISCOVERY TEST WITH GAPS:")
print(f"Styles: {result['dominant_styles']}")
print(f"Gaps: {result['gaps']}")
