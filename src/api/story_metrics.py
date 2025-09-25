"""
Story Development Metrics Module
Patent-Pending Algorithmic Assessment of Documentary Narrative Structure
"""

import re
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict

class StoryMetricsAnalyzer:
    """Calculate quantitative metrics for documentary story development"""
    
    def __init__(self):
        # Essential documentary elements for completeness scoring
        self.essential_elements = {
            'protagonist': {
                'weight': 15,
                'indicators': ['main character', 'protagonist', 'follows', 'subject', 'journalist', 'reporter'],
                'depth_check': lambda text: len(re.findall(r'\b(I|we|they|she|he)\b.*?(investigate|uncover|discover)', text, re.I)) > 0
            },
            'conflict': {
                'weight': 15,
                'indicators': ['conflict', 'struggle', 'versus', 'against', 'tension', 'murder', 'corruption'],
                'depth_check': lambda text: len(re.findall(r'(but|however|despite|although|versus)', text, re.I)) > 2
            },
            'stakes': {
                'weight': 15,
                'indicators': ['at stake', 'consequences', 'risk', 'matter', 'important', 'justice', 'truth'],
                'depth_check': lambda text: 'if' in (text or '').lower() and ('then' in (text or '').lower() or 'will' in (text or '').lower())
            },
            'access': {
                'weight': 15,
                'indicators': ['exclusive', 'access', 'inside', 'unprecedented', 'never before', 'personal'],
                'depth_check': lambda text: len(re.findall(r'(interview|footage|documents|archives)', text, re.I)) > 1
            },
            'transformation': {
                'weight': 15,
                'indicators': ['change', 'transform', 'become', 'realize', 'discover', 'journey'],
                'depth_check': lambda text: 'from' in (text or '').lower() and 'to' in (text or '').lower()
            },
            'evidence': {
                'weight': 15,
                'indicators': ['footage', 'documents', 'photos', 'records', 'evidence', 'proof'],
                'depth_check': lambda text: len(re.findall(r'\d{4}|\d+ years?|archiv|document', text, re.I)) > 2
            },
            'universal_theme': {
                'weight': 10,
                'indicators': ['about', 'explores', 'examines', 'questions', 'humanity', 'society'],
                'depth_check': lambda text: len((text or '').split()) > 50 and 'why' in (text or '').lower()
            }
        }
        
        # Successful documentary patterns for matching
        self.documentary_patterns = {
            'The Jinx': {
                'markers': ['true crime', 'investigation', 'multiple timeline', 'complex web', 'revelation'],
                'structure': ['mystery', 'investigation', 'confrontation', 'revelation']
            },
            'Making a Murderer': {
                'markers': ['injustice', 'legal system', 'wrongful', 'corruption', 'small town'],
                'structure': ['injustice revealed', 'investigation deepens', 'system exposed']
            },
            'The Act of Killing': {
                'markers': ['perpetrator', 'reenactment', 'confronting past', 'genocide', 'memory'],
                'structure': ['approach subjects', 'reveal through recreation', 'psychological journey']
            },
            'Free Solo': {
                'markers': ['personal challenge', 'physical feat', 'preparation', 'risk death'],
                'structure': ['establish challenge', 'preparation journey', 'climactic attempt']
            }
        }
    
    def calculate_completeness_index(self, deck_text: str, conversation_data: Dict) -> Dict:
        """Calculate how complete the story elements are (0-100)"""
        
        scores = {}
        total_score = 0
        
        # Combine deck and conversation answers for analysis
        full_text = (deck_text or '').lower() 
        for answer in conversation_data.get('answers', []):
            if answer.get('answer_text'):
                full_text += ' ' + (answer.get('answer_text') or '').lower()
        
        # Score each essential element
        for element, config in self.essential_elements.items():
            element_score = 0
            
            # Check for presence (40% of element score)
            for indicator in config['indicators']:
                if indicator in full_text:
                    element_score += 0.4 * config['weight']
                    break
            
            # Check for depth (60% of element score)
            if config['depth_check'](full_text):
                element_score += 0.6 * config['weight']
            
            scores[element] = element_score
            total_score += element_score
        
        return {
            'total_score': min(100, total_score),
            'element_scores': scores,
            'missing_elements': [k for k, v in scores.items() if v < 5],
            'strong_elements': [k for k, v in scores.items() if v > 10]
        }
    
    def calculate_coherence_score(self, deck_text: str, conversation_data: Dict) -> Dict:
        """Calculate narrative coherence through element relationships (0-100)"""
        
        # Extract entities and relationships
        entities = self._extract_entities(deck_text)
        relationships = defaultdict(list)
        
        # Build relationship graph
        for answer in conversation_data.get('answers', []):
            text = answer.get('answer_text', '')
            # Find connections between entities
            for entity1 in entities:
                for entity2 in entities:
                    if entity1 != entity2:
                        if entity1 in text and entity2 in text:
                            distance = abs(text.index(entity1) - text.index(entity2))
                            if distance < 100:  # Close proximity suggests relationship
                                relationships[entity1].append((entity2, 1.0 / (distance + 1)))
        
        # Calculate coherence metrics
        num_entities = len(entities)
        num_connections = sum(len(v) for v in relationships.values())
        
        if num_entities == 0:
            coherence_score = 0
        elif num_entities > 20:  # Too many entities (like Bad Grandma's 45 names)
            penalty = min(50, (num_entities - 20) * 2)
            base_score = min(50, num_connections * 2)
            coherence_score = max(0, base_score - penalty)
        else:
            # Good range of entities
            connectivity_ratio = num_connections / max(1, num_entities * (num_entities - 1) / 2)
            coherence_score = min(100, connectivity_ratio * 100)
        
        return {
            'score': coherence_score,
            'num_entities': num_entities,
            'num_connections': num_connections,
            'narrative_focus': 'scattered' if num_entities > 20 else 'focused' if num_entities < 5 else 'balanced',
            'recommendation': self._get_coherence_recommendation(num_entities, coherence_score)
        }
    
    def track_development_velocity(self, conversation_data: Dict) -> Dict:
        """Track how quickly gaps close during conversation (0-100)"""
        
        gap_closures = []
        velocities = []
        breakthrough_turn = None
        
        # Analyze each conversation turn
        for i, answer in enumerate(conversation_data.get('answers', [])):
            answer_text = (answer.get('answer_text') or '').lower()
            turn_num = i + 1
            
            # Calculate gap closure for this turn
            closure_score = 0
            
            # Check for key breakthrough indicators
            if any(word in answer_text for word in ['realize', 'actually', 'truth', 'discover']):
                closure_score += 20
                if not breakthrough_turn:
                    breakthrough_turn = turn_num
            
            # Check for specific details added
            if len(answer_text.split()) > 50:
                closure_score += 10
            
            # Check for personal connection
            if any(word in answer_text for word in ['my', 'our', 'family', 'personal']):
                closure_score += 15
                
            gap_closures.append(closure_score)
            
            # Calculate velocity (change from previous turn)
            if i > 0:
                velocity = closure_score - gap_closures[i-1]
                velocities.append(velocity)
        
        # Calculate overall velocity score
        total_closure = sum(gap_closures)
        avg_velocity = np.mean(velocities) if velocities else 0
        
        # Score based on total progress and consistency
        if total_closure > 60:
            base_score = 70
        elif total_closure > 40:
            base_score = 50
        else:
            base_score = 30
            
        # Adjust for velocity pattern
        if avg_velocity > 0:  # Accelerating
            velocity_score = min(100, base_score + 20)
        elif breakthrough_turn:  # Had breakthrough
            velocity_score = min(100, base_score + 15)
        else:
            velocity_score = base_score
        
        return {
            'score': velocity_score,
            'gap_closures_per_turn': gap_closures,
            'breakthrough_turn': breakthrough_turn,
            'pattern': self._identify_velocity_pattern(gap_closures),
            'total_gaps_closed': total_closure
        }
    
    def calculate_pattern_match(self, deck_text: str, conversation_data: Dict) -> Dict:
        """Compare story structure to successful documentaries (0-100)"""
        
        full_text = (deck_text or '').lower() 
        for answer in conversation_data.get('answers', []):
            if answer.get('answer_text'):
                full_text += ' ' + (answer.get('answer_text') or '').lower()
        
        best_match = None
        best_score = 0
        
        for doc_name, pattern in self.documentary_patterns.items():
            score = 0
            matches = []
            
            # Check for marker words
            for marker in pattern['markers']:
                if marker in full_text:
                    score += 15
                    matches.append(marker)
            
            # Check structural elements
            for structure_element in pattern['structure']:
                if any(word in structure_element for word in full_text.split()[:100]):
                    score += 10
            
            if score > best_score:
                best_score = score
                best_match = {
                    'documentary': doc_name,
                    'score': min(100, score),
                    'matched_elements': matches,
                    'structure_pattern': pattern['structure']
                }
        
        return {
            'best_match': best_match,
            'percentage': best_match['score'] if best_match else 0,
            'recommendation': self._get_pattern_recommendation(best_match) if best_match else None
        }
    
    def generate_metrics_summary(self, deck_text: str, conversation_data: Dict) -> Dict:
        """Generate complete metrics analysis"""
        
        completeness = self.calculate_completeness_index(deck_text, conversation_data)
        coherence = self.calculate_coherence_score(deck_text, conversation_data)
        velocity = self.track_development_velocity(conversation_data)
        pattern = self.calculate_pattern_match(deck_text, conversation_data)
        
        return {
            'completeness': completeness,
            'coherence': coherence,
            'velocity': velocity,
            'pattern_match': pattern,
            'overall_readiness': self._calculate_overall_readiness(
                completeness['total_score'],
                coherence['score'],
                velocity['score'],
                pattern['percentage']
            )
        }
    
    # Helper methods
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        # Simple extraction - could be enhanced with spaCy
        entities = []
        # Look for capitalized words (likely names)
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and word.lower() not in ['the', 'a', 'an', 'this', 'that']:
                entities.append(word)
        return list(set(entities))[:30]  # Limit to 30 entities
    
    def _get_coherence_recommendation(self, num_entities: int, score: float) -> str:
        if num_entities > 20:
            return "Too many story elements. Focus on one protagonist to guide us through this complex web."
        elif score < 50:
            return "Story elements feel disconnected. Find the thread that links all pieces together."
        else:
            return "Good narrative coherence. Elements connect well."
    
    def _identify_velocity_pattern(self, closures: List[float]) -> str:
        if not closures:
            return "No pattern"
        if closures[-1] > closures[0]:
            return "Accelerating (good momentum)"
        elif any(c > 15 for c in closures[2:]):
            return "Breakthrough achieved"
        else:
            return "Steady development"
    
    def _get_pattern_recommendation(self, match: Dict) -> str:
        if not match:
            return "No clear documentary pattern detected"
        
        doc = match['documentary']
        score = match['score']
        
        if score > 70:
            return f"Strong alignment with '{doc}' structure. Study how that film handled similar elements."
        else:
            return f"Partial match with '{doc}'. Consider what made that film successful."
    
    def _calculate_overall_readiness(self, completeness: float, coherence: float, 
                                     velocity: float, pattern: float) -> Dict:
        """Calculate overall production readiness"""
        
        avg_score = (completeness + coherence + velocity + pattern) / 4
        
        if avg_score >= 75:
            readiness = "Ready for production"
            next_step = "Move to treatment and funding proposals"
        elif avg_score >= 50:
            readiness = "Needs development"
            next_step = "Address gaps before moving forward"
        else:
            readiness = "Early stage"
            next_step = "Continue story development sessions"
        
        return {
            'score': avg_score,
            'status': readiness,
            'next_step': next_step
        }
