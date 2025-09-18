import sys
sys.path.append('src/api')
from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer

analyzer = DocumentaryStyleAnalyzer()

# Test with STRONG argument text
argument_text = """
This documentary will prove that climate change threatens humanity. 
We argue that fossil fuel companies deliberately misled the public.
Through extensive data analysis and expert testimony, we demonstrate 
the urgent crisis. Research clearly shows rising temperatures. 
Statistics reveal accelerating ice melt. Evidence is overwhelming.
We must convince policymakers to act immediately.
"""

result = analyzer.analyze_pitch(argument_text)
print("ARGUMENT-DRIVEN TEST:")
print(f"Styles: {result['dominant_styles']}")
print(f"Gaps: {[g['type'] for g in result['gaps']]}")
print(f"Confidence: {result['analysis_confidence']}")
