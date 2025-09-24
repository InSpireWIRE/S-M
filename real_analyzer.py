"""
Real documentary analysis using academic frameworks
Not keyword counting bullshit
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from real_frameworks import *
import re

class RealStructureAnalyzer:
    """Uses actual three-act structure theory"""
    
    def __init__(self):
        self.structure = THREE_ACT_STRUCTURE
        self.propp = PROPP_FUNCTIONS
        
    def analyze_structure(self, chunks):
        """Map chunks to actual story structure"""
        analysis = {
            'found_beats': {},
            'missing_beats': [],
            'act_distribution': {'act_1': 0, 'act_2': 0, 'act_3': 0},
            'propp_functions': [],
            'structure_score': 0.0
        }
        
        total_chunks = len(chunks)
        if total_chunks == 0:
            return analysis
            
        for i, chunk in enumerate(chunks):
            position = i / total_chunks
            content = chunk.get('content', '').lower()
            
            # Determine act based on position
            if position <= 0.25:
                act = 'act_1_setup'
                analysis['act_distribution']['act_1'] += 1
            elif position <= 0.75:
                act = 'act_2_confrontation'
                analysis['act_distribution']['act_2'] += 1
            else:
                act = 'act_3_resolution'
                analysis['act_distribution']['act_3'] += 1
            
            # Check for story beats in appropriate position
            for beat_name, (start, end) in self.structure[act]['beats'].items():
                if start <= position <= end:
                    # This chunk is in position for this beat
                    analysis['found_beats'][beat_name] = position
            
            # Check for Propp functions
            for func_name, func_data in self.propp.items():
                if any(marker in content for marker in func_data['markers']):
                    analysis['propp_functions'].append({
                        'function': func_name,
                        'position': position,
                        'description': func_data['description']
                    })
        
        # Calculate what's missing
        all_beats = []
        for act_data in self.structure.values():
            all_beats.extend(act_data['beats'].keys())
        
        analysis['missing_beats'] = [beat for beat in all_beats 
                                     if beat not in analysis['found_beats']]
        
        # Calculate structure score (0-100)
        beats_found = len(analysis['found_beats'])
        total_beats = len(all_beats)
        analysis['structure_score'] = (beats_found / total_beats) * 100 if total_beats > 0 else 0
        
        return analysis


class RealEmotionalAnalyzer:
    """Uses actual sentiment analysis, not word counting"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.emotions = EMOTION_CATEGORIES
        
    def analyze_emotions(self, chunks):
        """Track real emotional arc through story"""
        analysis = {
            'emotional_arc': [],
            'dominant_emotions': {},
            'emotional_volatility': 0.0,
            'sentiment_progression': []
        }
        
        for chunk in chunks:
            content = chunk.get('content', '')
            
            # Get real sentiment scores
            sentiment = self.vader.polarity_scores(content)
            analysis['sentiment_progression'].append(sentiment)
            
            # Track specific emotions
            chunk_emotions = {}
            for emotion, words in self.emotions.items():
                all_words = words['basic'] + words['intense'] + words['mild']
                count = sum(1 for word in all_words if word in content.lower())
                if count > 0:
                    chunk_emotions[emotion] = count
            
            analysis['emotional_arc'].append({
                'sentiment': sentiment,
                'emotions': chunk_emotions,
                'compound': sentiment['compound']
            })
        
        # Calculate emotional volatility (how much emotions swing)
        if len(analysis['sentiment_progression']) > 1:
            compounds = [s['compound'] for s in analysis['sentiment_progression']]
            volatility = sum(abs(compounds[i] - compounds[i-1]) 
                           for i in range(1, len(compounds)))
            analysis['emotional_volatility'] = volatility / (len(compounds) - 1)
        
        # Find dominant emotions across all chunks
        all_emotions = {}
        for arc_point in analysis['emotional_arc']:
            for emotion, count in arc_point['emotions'].items():
                all_emotions[emotion] = all_emotions.get(emotion, 0) + count
        
        # Sort by frequency
        analysis['dominant_emotions'] = dict(sorted(all_emotions.items(), 
                                                   key=lambda x: x[1], 
                                                   reverse=True)[:3])
        
        return analysis


def compare_old_vs_new(chunks):
    """Show the difference between bullshit and real analysis"""
    
    # Old bullshit way (what you have now)
    emotion_words = sum(1 for chunk in chunks 
                       for word in ['feel', 'felt', 'emotion', 'heart']
                       if word in chunk.get('content', '').lower())
    old_score = min(10, emotion_words // 3)
    
    # New real way
    analyzer = RealEmotionalAnalyzer()
    real_analysis = analyzer.analyze_emotions(chunks)
    
    print("OLD BULLSHIT: Emotional archaeology score =", old_score)
    print("NEW REAL: Emotional volatility =", real_analysis['emotional_volatility'])
    print("NEW REAL: Dominant emotions =", real_analysis['dominant_emotions'])
    print("NEW REAL: Sentiment progression = [compound scores from -1 to +1]")
    
    return old_score, real_analysis
