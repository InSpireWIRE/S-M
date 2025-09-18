import spacy
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import Counter

class DocumentaryStyleAnalyzer:
    """
    Documentary style detection based on established film theory.
    Analyzes pitch text to identify documentary approaches.
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            self.nlp = spacy.load("en_core_web_sm")
        
        self.style_patterns = self._initialize_patterns()
        self.min_confidence = 0.15
        
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize detection patterns based on established documentary theory"""
        return {
            'ARGUMENT-DRIVEN': {
                'claim_verbs': ['argues', 'demonstrates', 'proves', 'shows', 'reveals', 
                              'establishes', 'confirms', 'validates', 'exposes'],
                'evidence_markers': ['data', 'research', 'study', 'statistics', 'expert', 
                                   'interview', 'footage', 'document', 'testimony'],
                'direct_address': ['you', 'we must', 'it is clear', 'obviously', 'certainly'],
                'problem_solution': ['problem', 'issue', 'crisis', 'solution', 'answer', 'resolve'],
                'production_methods': ['expert interviews', 'archival footage', 'data visualization', 
                                      'narrator', 'narration', 'voice-over', 'research footage'],
                'authority_markers': ['leading expert', 'professor', 'researcher', 'study author']
            },
            
            'DISCOVERY-FOCUSED': {
                'observation_markers': ['observe', 'watch', 'witness', 'see', 'notice', 
                                      'happening', 'unfold', 'emerge'],
                'present_tense': ['is', 'are', 'happening', 'occurring', 'developing'],
                'process_words': ['process', 'development', 'evolution', 'change', 'growth'],
                'non_intervention': ['without interference', 'naturally', 'spontaneous', 
                                   'organic', 'authentic', 'real-time'],
                'production_methods': ['cinema verite', 'fly on the wall', 'follow for months',
                                      'embed with', 'no interviews', 'observational', 'longitudinal'],
                'access_markers': ['exclusive access', 'intimate access', 'behind the scenes']
            },
            
            'ENCOUNTER-BASED': {
                'filmmaker_presence': ['I', 'we', 'my', 'our', 'filmmaker', 'director'],
                'interaction_verbs': ['interview', 'speak with', 'talk to', 'meet', 
                                    'engage', 'collaborate', 'work with'],
                'relationship_words': ['relationship', 'connection', 'encounter', 
                                     'dialogue', 'conversation', 'exchange'],
                'production_methods': ['on camera', 'my journey', 'I travel', 'I investigate',
                                      'personal quest', 'confrontation', 'my interviews with'],
                'relationship_markers': ['my connection', 'personal stake', 'my history with']
            }
        }
    
    def analyze_pitch(self, text: str) -> Dict:
        """Main analysis function"""
        doc = self.nlp(text)
        
        style_scores = {}
        for style_name, patterns in self.style_patterns.items():
            score = self._calculate_style_score(text, doc, patterns)
            if score > self.min_confidence:
                style_scores[style_name] = score
        
        dominant_styles = sorted(style_scores.keys(), 
                               key=lambda x: style_scores[x], 
                               reverse=True)[:2]
        
        gaps = self._identify_gaps(text, dominant_styles)
        
        return {
            'dominant_styles': dominant_styles,
            'style_scores': style_scores,
            'production_methods': self.detect_production_complexity(text),
            'gaps': gaps,
            'analysis_confidence': max(style_scores.values()) if style_scores else 0.0
        }
    
    def _calculate_style_score(self, text: str, doc, patterns: Dict) -> float:
        """Calculate how strongly text matches a style"""
        text_lower = text.lower()
        scores = []
        
        for pattern_type, pattern_list in patterns.items():
            matches = 0
            for pattern in pattern_list:
                # Check for word stem matches, not exact matches
                if pattern.lower() in text_lower:
                    matches += 1
                # Also check for word roots (prove/proves/proving)
                elif pattern.lower().rstrip('s').rstrip('es') in text_lower:
                    matches += 1
                elif text_lower.find(pattern.lower()[:4]) >= 0 and len(pattern) > 4:
                    matches += 0.5  # Partial match for word stems
            
            if pattern_list:
                scores.append(matches / len(pattern_list))
        
        return np.mean(scores) if scores else 0.0
    
    def _identify_gaps(self, text: str, dominant_styles: List[str]) -> List[Dict]:
        """Identify what's missing based on detected style"""
        gaps = []
        text_lower = text.lower()
        
        if 'ARGUMENT-DRIVEN' in dominant_styles:
            if not any(word in text_lower for word in ['counter', 'opposition', 'however', 'although']):
                gaps.append({
                    'type': 'no_counterargument_consideration',
                    'severity': 'medium',
                    'suggestion': 'Consider addressing opposing viewpoints'
                })
            if 'evidence' not in text_lower and 'data' not in text_lower:
                gaps.append({
                    'type': 'missing_evidence_strategy',
                    'severity': 'high',
                    'suggestion': 'Explain how you will present evidence'
                })
            if not any(word in text_lower for word in ['interview', 'expert', 'testimony']):
                gaps.append({
                    'type': 'no_authority_voices',
                    'severity': 'high',
                    'suggestion': 'Identify expert voices to support argument'
                })
        
        if 'DISCOVERY-FOCUSED' in dominant_styles:
            if not any(time in text_lower for time in ['months', 'years', 'weeks', 'time']):
                gaps.append({
                    'type': 'insufficient_observation_time',
                    'severity': 'medium',
                    'suggestion': 'Specify observation timeframe'
                })
            if not any(word in text_lower for word in ['access', 'permission', 'embed']):
                gaps.append({
                    'type': 'unclear_access',
                    'severity': 'high',
                    'suggestion': 'Explain how you will gain observational access'
                })
        
        # Universal gaps that apply to ALL documentaries regardless of style
        if 'conflict' not in text_lower and 'obstacle' not in text_lower and 'challenge' not in text_lower and 'against' not in text_lower:
            gaps.append({
                'type': 'missing_conflict',
                'severity': 'high',
                'suggestion': 'Identify the central conflict or obstacles'
            })
        
        if 'change' not in text_lower and 'transform' not in text_lower and 'journey' not in text_lower and 'become' not in text_lower:
            gaps.append({
                'type': 'no_transformation',
                'severity': 'high',
                'suggestion': 'Describe what changes from beginning to end'
            })
        
        if 'stakes' not in text_lower and 'risk' not in text_lower and 'lose' not in text_lower and 'fail' not in text_lower:
            gaps.append({
                'type': 'no_stakes',
                'severity': 'high',
                'suggestion': 'Clarify what is at risk or why this matters'
            })
        
        if 'access' not in text_lower and 'permission' not in text_lower and 'let me' not in text_lower:
            gaps.append({
                'type': 'unclear_access',
                'severity': 'medium',
                'suggestion': 'Explain your unique access to the story'
            })
        
        return gaps

    def detect_production_complexity(self, text: str) -> Dict:
        """Detect production methods and complexity"""
        methods_found = []
        
        production_indicators = {
            'interviews': ['interview', 'conversation with', 'speak with'],
            'verite': ['verite', 'observational', 'fly on wall'],
            'archival': ['archival', 'archive footage', 'historical footage'],
            'recreation': ['recreation', 'reenactment', 'dramatization'],
            'user_generated': ['social media', 'user submitted', 'crowdsourced'],
            'animation': ['animated', 'animation', 'graphic'],
            'personal_archive': ['home videos', 'personal footage', 'family films']
        }
        
        text_lower = text.lower()
        for method, indicators in production_indicators.items():
            if any(ind in text_lower for ind in indicators):
                methods_found.append(method)
        
        return {
            'methods': methods_found,
            'complexity': 'simple' if len(methods_found) <= 2 else 'complex',
            'is_hybrid': len(methods_found) > 3
        }
    
    def detect_narrative_structure(self, text: str) -> Dict:
        """Second layer - detect narrative structure"""
        doc = self.nlp(text.lower())
        
        structures = {
            'todorov': 0.0,
            'circular': 0.0,
            'processual': 0.0,
            'ascending': 0.0,
            'fragmentary': 0.0
        }
        
        # Todorov detection
        todorov_patterns = ['before', 'then', 'after', 'changed', 'problem', 'resolved']
        for token in doc:
            if token.text in todorov_patterns:
                structures['todorov'] += 0.15
        
        # Look for phrases indicating stages
        text_lower = text.lower()
        if 'used to be' in text_lower or 'everything changed' in text_lower:
            structures['todorov'] += 0.3
        if 'problem' in text_lower and 'solution' in text_lower:
            structures['todorov'] += 0.2
            
        # Circular detection  
        if any(phrase in text_lower for phrase in ['full circle', 'return to', 'back where']):
            structures['circular'] += 0.7
            
        # Processual detection
        if any(word in text_lower for word in ['ongoing', 'unfolding', 'continuing']):
            structures['processual'] += 0.5
        if 'as it happens' in text_lower or 'still developing' in text_lower:
            structures['processual'] += 0.3
            
        # Get highest confidence
        max_structure = max(structures.items(), key=lambda x: x[1])
        
        return {
            'structure': max_structure[0] if max_structure[1] > 0.3 else 'unknown',
            'confidence': max_structure[1],
            'all_scores': structures
        }
    
    def detect_narrative_gaps(self, text: str, structure: str) -> List[str]:
        """Detect what's missing based on structure"""
        gaps = []
        text_lower = text.lower()
        
        if structure == 'todorov':
            # Check for Todorov elements
            if not any(word in text_lower for word in ['before', 'originally', 'used to', 'initially']):
                gaps.append('missing_equilibrium')
            if not any(word in text_lower for word in ['changed', 'happened', 'disrupted', 'event']):
                gaps.append('unclear_disruption')
            if not any(word in text_lower for word in ['realized', 'discovered', 'understood']):
                gaps.append('absent_recognition')
            if not any(word in text_lower for word in ['trying', 'attempting', 'working to', 'fixing']):
                gaps.append('no_repair_attempt')
            if not any(word in text_lower for word in ['finally', 'ultimately', 'ends', 'resolves']):
                gaps.append('unresolved_ending')
                
        return gaps
    
    def detect_style_structure_tensions(self, style: str, structure: str) -> List[Dict]:
        """Find productive tensions between style and structure"""
        tensions = []
        
        tension_map = {
            ('discovery_focused', 'todorov'): {
                'tension': "You're discovering but planning for a neat ending",
                'opportunity': "What if discovery leads somewhere unexpected?",
                'choices': ["Follow discovery wherever it goes", "Use structure as a guide", "Make the tension your method"]
            },
            ('argument_driven', 'processual'): {
                'tension': "You're making a point but just following along",
                'opportunity': "The gap between thesis and reality could be powerful",
                'choices': ["Let your point emerge from events", "Use ongoing events as evidence", "Question your own argument"]
            },
            ('encounter_based', 'circular'): {
                'tension': "Personal encounters but returning to start",
                'opportunity': "The return could reveal how encounters changed you",
                'choices': ["Show transformation through encounters", "Use circularity to highlight personal growth", "Question if you can truly return"]
            }
        }
        
        # Convert style to match tension_map keys
        style_key = style.lower().replace('-', '_')
        key = (style_key, structure)
        if key in tension_map:
            tensions.append(tension_map[key])
            
        return tensions