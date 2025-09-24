"""
Test to show the difference between bullshit word counting and real analysis
"""

from real_analyzer import RealStructureAnalyzer, RealEmotionalAnalyzer
import json

# Create fake chunks to test (simulating what would come from your deck)
test_chunks = [
    {
        'content': "Veronica Butler was a victim who suffered terribly. She was killed in a brutal attack.",
        'chunk_type': 'character'
    },
    {
        'content': "The story begins when Grandma Tifany starts to manipulate everyone around her using fear and money.",
        'chunk_type': 'conflict'
    },
    {
        'content': "In the middle, everything falls apart. The investigation reveals shocking truths about the murders.",
        'chunk_type': 'stakes'
    },
    {
        'content': "Finally, justice arrives but the damage is done. The community will never be the same.",
        'chunk_type': 'resolution'
    }
]

print("="*60)
print("COMPARING OLD BULLSHIT VS REAL ANALYSIS")
print("="*60)

# OLD WAY (what you have now)
print("\n1. OLD EMOTION ANALYSIS (keyword counting):")
emotion_words = sum(1 for chunk in test_chunks 
                   for word in ['feel', 'felt', 'emotion', 'heart', 'soul', 'fear', 'love']
                   if word in chunk['content'].lower())
old_emotion_score = min(10, emotion_words // 3)
print(f"   Counted {emotion_words} emotion words / 3 = {old_emotion_score}/10")
print("   That's it. That's the whole analysis.")

# NEW WAY
print("\n2. NEW EMOTION ANALYSIS (real sentiment analysis):")
emotional_analyzer = RealEmotionalAnalyzer()
emotional_results = emotional_analyzer.analyze_emotions(test_chunks)

print("   Sentiment progression through story:")
for i, sentiment in enumerate(emotional_results['sentiment_progression']):
    print(f"      Chunk {i+1}: Compound={sentiment['compound']:.3f} "
          f"(Pos:{sentiment['pos']:.2f}, Neg:{sentiment['neg']:.2f}, Neutral:{sentiment['neu']:.2f})")

print(f"   Emotional volatility: {emotional_results['emotional_volatility']:.3f}")
print(f"   Dominant emotions: {emotional_results['dominant_emotions']}")

print("\n" + "="*60)

# OLD STRUCTURE ANALYSIS
print("\n3. OLD STRUCTURE ANALYSIS (counting keywords):")
structure_words = sum(1 for chunk in test_chunks 
                      for word in ['begins', 'middle', 'end', 'finally']
                      if word in chunk['content'].lower())
print(f"   Found {structure_words} structure words. That's it.")

# NEW STRUCTURE ANALYSIS
print("\n4. NEW STRUCTURE ANALYSIS (real three-act mapping):")
structure_analyzer = RealStructureAnalyzer()
structure_results = structure_analyzer.analyze_structure(test_chunks)

print(f"   Act distribution: {structure_results['act_distribution']}")
print(f"   Structure score: {structure_results['structure_score']:.1f}%")
print(f"   Found beats: {list(structure_results['found_beats'].keys())}")
print(f"   Missing beats: {structure_results['missing_beats'][:5]}...")  # First 5
print(f"   Propp functions detected: {[f['function'] for f in structure_results['propp_functions']]}")

print("\n" + "="*60)
print("Which analysis would you rather have for your documentary?")
print("="*60)
