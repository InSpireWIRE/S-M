import os
import re
import json
import openai
import hashlib
from typing import List, Dict, Tuple
from dataclasses import dataclass
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
import pdfplumber

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Initialize Supabase
url = "https://izhvyvicvbbuiconxitm.supabase.co"
key = "sb_publishable_0K-bNGkZJiBsSMS__3AG8w_j5n-UeaX"
supabase: Client = create_client(url, key)

# Initialize OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

@dataclass
class StoryChunk:
    text: str
    chunk_type: str  # 'setup', 'conflict', 'resolution', 'character', 'theme'
    importance: float
    entities: List[str]
    emotions: List[str]
    
@dataclass 
class Relationship:
    entity1: str
    entity2: str
    relationship_type: str  # 'family', 'romantic', 'antagonistic', 'professional'
    strength: float
    evidence: List[str]

class StoryIntelligenceEngine:
    def __init__(self):
        self.propp_functions = [
            "absentation", "interdiction", "violation", "reconnaissance", "delivery",
            "trickery", "complicity", "villainy", "mediation", "beginning_counteraction",
            "departure", "first_function_of_donor", "hero_reaction", "receipt_of_agent",
            "spatial_transference", "struggle", "branding", "victory", "liquidation",
            "return", "pursuit", "rescue", "unrecognized_arrival", "unfounded_claims",
            "difficult_task", "solution", "recognition", "exposure", "transfiguration",
            "punishment", "wedding"
        ]
        
        self.story_beats = {
            'opening_image': 'First impression of protagonist\'s world',
            'inciting_incident': 'Event that sets story in motion',
            'plot_point_1': 'End of first act, major change',
            'midpoint': 'Major revelation or shift',
            'plot_point_2': 'End of second act, all seems lost',
            'climax': 'Final confrontation or revelation',
            'resolution': 'New normal established'
        }

    def extract_entities_with_context(self, text: str) -> Dict[str, List[str]]:
        """Extract entities with better context awareness"""
        
        # Name patterns (enhanced)
        name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Full names
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Multi-part names
            r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\b',  # Titles with names
        ]
        
        # Location patterns (enhanced)
        location_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "in Location"
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "at Location"
            r'\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "from Location"
        ]
        
        # Organization patterns
        org_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Company|Corp|Inc|Ltd|Organization)\b',
            r'\bthe\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Department|Division|Team)\b',
        ]
        
        entities = {
            'names': [],
            'locations': [],
            'organizations': [],
            'concepts': []
        }
        
        # Extract names
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            entities['names'].extend(matches)
        
        # Extract locations
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            entities['locations'].extend(matches)
        
        # Extract organizations
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            entities['organizations'].extend(matches)
        
        # Extract key concepts (capitalized important terms)
        concept_pattern = r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b'
        potential_concepts = re.findall(concept_pattern, text)
        
        # Filter out common words and already captured entities
        common_words = {'The', 'This', 'That', 'These', 'Those', 'When', 'Where', 'Why', 'How', 'What'}
        all_found_entities = entities['names'] + entities['locations'] + entities['organizations']
        
        for concept in potential_concepts:
            if (concept not in common_words and 
                concept not in all_found_entities and 
                len(concept) > 2):
                entities['concepts'].append(concept)
        
        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set(entities[key]))
            entities[key] = [e for e in entities[key] if len(e.strip()) > 1]
        
        return entities

    def extract_relationships_detailed(self, text: str, entities: Dict[str, List[str]]) -> List[Relationship]:
        """Extract detailed relationships between entities"""
        relationships = []
        all_entities = []
        
        # Flatten all entities
        for entity_type, entity_list in entities.items():
            all_entities.extend(entity_list)
        
        # Relationship indicator patterns
        relationship_patterns = {
            'family': [
                r'(\w+)(?:\s+\w+)?\s+(?:is|was)\s+(?:the\s+)?(?:father|mother|brother|sister|son|daughter|parent|child|husband|wife|spouse)\s+of\s+(\w+)',
                r'(\w+)(?:\s+\w+)?\s+and\s+(\w+)(?:\s+\w+)?\s+(?:are|were)\s+(?:married|siblings|family|related)',
                r'(\w+)(?:\'s|\s+\w+\'s)\s+(?:father|mother|brother|sister|son|daughter|parent|child|husband|wife|spouse)\s+(\w+)'
            ],
            'romantic': [
                r'(\w+)(?:\s+\w+)?\s+(?:loves|loved|dating|married|engaged to)\s+(\w+)',
                r'(\w+)(?:\s+\w+)?\s+and\s+(\w+)(?:\s+\w+)?\s+(?:are|were)\s+(?:in love|dating|together|romantic)',
                r'(\w+)(?:\s+\w+)?\s+(?:kissed|hugged|embraced)\s+(\w+)'
            ],
            'antagonistic': [
                r'(\w+)(?:\s+\w+)?\s+(?:fought|fights|battles|opposes|hates|enemies|rivals)\s+(?:with\s+|against\s+)?(\w+)',
                r'(\w+)(?:\s+\w+)?\s+and\s+(\w+)(?:\s+\w+)?\s+(?:are|were)\s+(?:enemies|rivals|opponents)',
                r'(\w+)(?:\s+\w+)?\s+(?:attacked|betrayed|defeated)\s+(\w+)'
            ],
            'professional': [
                r'(\w+)(?:\s+\w+)?\s+(?:works for|employed by|boss of|manages|supervises)\s+(\w+)',
                r'(\w+)(?:\s+\w+)?\s+and\s+(\w+)(?:\s+\w+)?\s+(?:work together|colleagues|partners|teammates)',
                r'(\w+)(?:\s+\w+)?\s+(?:hired|fired|promoted)\s+(\w+)'
            ],
            'friendship': [
                r'(\w+)(?:\s+\w+)?\s+(?:is friends with|befriended|close to)\s+(\w+)',
                r'(\w+)(?:\s+\w+)?\s+and\s+(\w+)(?:\s+\w+)?\s+(?:are|were)\s+(?:friends|close|allies)',
                r'(\w+)(?:\s+\w+)?\s+(?:helped|supported|trusted)\s+(\w+)'
            ]
        }
        
        # Extract relationships using patterns
        for rel_type, patterns in relationship_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity1, entity2 = match[0], match[1]
                    
                    # Validate entities exist in our extracted entities
                    if any(entity1.lower() in e.lower() for e in all_entities) and \
                       any(entity2.lower() in e.lower() for e in all_entities):
                        
                        # Calculate relationship strength based on frequency and context
                        strength = self.calculate_relationship_strength(text, entity1, entity2, rel_type)
                        
                        # Find evidence sentences
                        evidence = self.find_relationship_evidence(text, entity1, entity2, rel_type)
                        
                        relationships.append(Relationship(
                            entity1=entity1,
                            entity2=entity2,
                            relationship_type=rel_type,
                            strength=strength,
                            evidence=evidence
                        ))
        
        # Remove duplicates and merge similar relationships
        relationships = self.deduplicate_relationships(relationships)
        
        return relationships

    def calculate_relationship_strength(self, text: str, entity1: str, entity2: str, rel_type: str) -> float:
        """Calculate the strength of a relationship based on context and frequency"""
        
        # Count mentions of both entities together
        pattern1 = rf'\b{re.escape(entity1)}\b.*?\b{re.escape(entity2)}\b'
        pattern2 = rf'\b{re.escape(entity2)}\b.*?\b{re.escape(entity1)}\b'
        
        mentions1 = len(re.findall(pattern1, text, re.IGNORECASE))
        mentions2 = len(re.findall(pattern2, text, re.IGNORECASE))
        total_mentions = mentions1 + mentions2
        
        # Base strength from frequency
        frequency_strength = min(1.0, total_mentions / 5.0)  # Max strength at 5+ mentions
        
        # Relationship type modifiers
        type_modifiers = {
            'family': 1.2,      # Family relationships are typically strong
            'romantic': 1.3,    # Romantic relationships are very important
            'antagonistic': 1.1, # Conflicts are dramatic
            'professional': 0.9, # Professional can be weaker
            'friendship': 1.0    # Baseline
        }
        
        # Context strength indicators
        strong_indicators = ['deeply', 'always', 'forever', 'never', 'completely', 'totally']
        context_strength = sum(1 for indicator in strong_indicators 
                             if indicator in text.lower()) * 0.1
        
        final_strength = (frequency_strength + context_strength) * type_modifiers.get(rel_type, 1.0)
        return min(1.0, final_strength)

    def find_relationship_evidence(self, text: str, entity1: str, entity2: str, rel_type: str) -> List[str]:
        """Find specific sentences that provide evidence for the relationship"""
        sentences = re.split(r'[.!?]+', text)
        evidence = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short fragments
                continue
                
            # Check if sentence contains both entities
            if (entity1.lower() in sentence.lower() and 
                entity2.lower() in sentence.lower()):
                evidence.append(sentence)
        
        return evidence[:3]  # Return up to 3 pieces of evidence

    def deduplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Remove duplicate relationships and merge similar ones"""
        unique_relationships = {}
        
        for rel in relationships:
            # Create a normalized key for deduplication
            entities_sorted = tuple(sorted([rel.entity1.lower(), rel.entity2.lower()]))
            key = (entities_sorted, rel.relationship_type)
            
            if key in unique_relationships:
                # Merge with existing relationship (keep higher strength)
                existing = unique_relationships[key]
                if rel.strength > existing.strength:
                    existing.strength = rel.strength
                # Combine evidence
                existing.evidence.extend(rel.evidence)
                existing.evidence = list(set(existing.evidence))  # Remove duplicates
            else:
                unique_relationships[key] = rel
        
        return list(unique_relationships.values())

    def analyze_text_chunks(self, text: str) -> List[StoryChunk]:
        """Break down text into meaningful story chunks"""
        
        # Split into paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        
        for i, paragraph in enumerate(paragraphs):
            # Analyze chunk type based on content
            chunk_type = self.classify_chunk_type(paragraph)
            
            # Calculate importance based on length, entities, and emotional content
            entities = self.extract_entities_with_context(paragraph)
            importance = self.calculate_chunk_importance(paragraph, entities)
            
            # Extract emotions/sentiment
            emotions = self.extract_emotions(paragraph)
            
            # Flatten entities for storage
            all_entities = []
            for entity_list in entities.values():
                all_entities.extend(entity_list)
            
            chunks.append(StoryChunk(
                text=paragraph,
                chunk_type=chunk_type,
                importance=importance,
                entities=all_entities,
                emotions=emotions
            ))
        
        return chunks

    def classify_chunk_type(self, text: str) -> str:
        """Classify what type of story element this chunk represents"""
        
        # Keywords for different story types
        setup_keywords = ['introduction', 'begin', 'start', 'first', 'initially', 'background']
        conflict_keywords = ['problem', 'conflict', 'challenge', 'struggle', 'fight', 'battle', 'against']
        resolution_keywords = ['solution', 'resolved', 'ended', 'finally', 'conclusion', 'result']
        character_keywords = ['character', 'person', 'personality', 'traits', 'described as']
        theme_keywords = ['theme', 'meaning', 'represents', 'symbolizes', 'significance']
        
        text_lower = text.lower()
        
        # Count keyword occurrences
        setup_score = sum(1 for kw in setup_keywords if kw in text_lower)
        conflict_score = sum(1 for kw in conflict_keywords if kw in text_lower)
        resolution_score = sum(1 for kw in resolution_keywords if kw in text_lower)
        character_score = sum(1 for kw in character_keywords if kw in text_lower)
        theme_score = sum(1 for kw in theme_keywords if kw in text_lower)
        
        # Determine highest scoring type
        scores = {
            'setup': setup_score,
            'conflict': conflict_score,
            'resolution': resolution_score,
            'character': character_score,
            'theme': theme_score
        }
        
        max_type = max(scores, key=scores.get)
        
        # If no clear winner, default based on structure
        if scores[max_type] == 0:
            return 'narrative'  # Default type
        
        return max_type

    def calculate_chunk_importance(self, text: str, entities: Dict[str, List[str]]) -> float:
        """Calculate how important this chunk is to the overall story"""
        
        # Base importance on length (longer chunks often more important)
        length_score = min(1.0, len(text) / 500)  # Normalize to max 1.0 at 500+ chars
        
        # Entity density (more entities = more important)
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        entity_score = min(1.0, total_entities / 10)  # Normalize to max 1.0 at 10+ entities
        
        # Emotional intensity indicators
        emotion_indicators = ['!', 'shocking', 'amazing', 'terrible', 'wonderful', 'devastating']
        emotion_score = min(1.0, sum(text.lower().count(indicator) for indicator in emotion_indicators) / 5)
        
        # Dialogue often important
        dialogue_score = 0.3 if '"' in text or "'" in text else 0
        
        # Combine scores
        importance = (length_score * 0.3 + 
                     entity_score * 0.4 + 
                     emotion_score * 0.2 + 
                     dialogue_score * 0.1)
        
        return min(1.0, importance)

    def extract_emotions(self, text: str) -> List[str]:
        """Extract emotional content from text"""
        
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'delighted', 'thrilled', 'cheerful'],
            'sadness': ['sad', 'depressed', 'melancholy', 'grief', 'sorrow', 'disappointed'],
            'anger': ['angry', 'furious', 'rage', 'mad', 'irritated', 'frustrated'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'startled'],
            'disgust': ['disgusted', 'repulsed', 'revolted', 'sickened'],
            'love': ['love', 'adore', 'cherish', 'treasure', 'devoted'],
            'hate': ['hate', 'despise', 'loathe', 'detest']
        }
        
        found_emotions = []
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_emotions.append(emotion)
        
        return found_emotions

    def generate_story_diagnostic(self, chunks: List[StoryChunk], all_entities: Dict[str, List[str]]) -> Dict:
        """Generate comprehensive story diagnostic"""
        
        # Structure analysis
        act_distribution = self.analyze_act_structure(chunks)
        story_beats = self.identify_story_beats(chunks)
        propp_functions = self.identify_propp_functions(chunks)
        
        # Character analysis
        character_development = self.analyze_character_development(chunks, all_entities)
        
        # Thematic analysis
        theme_analysis = self.analyze_themes(chunks)
        
        # Conflict analysis
        conflict_analysis = self.analyze_conflicts(chunks)
        
        # Emotional analysis
        emotional_arc = self.analyze_emotional_arc(chunks)
        
        diagnostic = {
            # Structure scores
            'structural_clarity': min(10, len(story_beats) * 1.5),
            'act_distribution': act_distribution,
            'story_beats_found': list(story_beats.keys()),
            'propp_functions_found': propp_functions,
            
            # Character scores
            'character_development': character_development,
            'character_count': len(all_entities.get('names', [])),
            
            # Theme and conflict
            'thematic_depth': theme_analysis['depth_score'],
            'conflict_specificity': conflict_analysis['specificity_score'],
            'transformation_markers': conflict_analysis['transformation_count'],
            
            # Emotional scores
            'emotional_volatility': emotional_arc['volatility'],
            'emotional_arc': emotional_arc['progression'],
            'dominant_emotions': emotional_arc['dominant'],
            
            # Advanced analysis
            'pattern_recognition': len(propp_functions),
            'perspective_diversity': min(10, len(set(all_entities.get('names', []))) * 2),
            'subtext_density': theme_analysis['subtext_score']
        }
        
        return diagnostic

    def analyze_act_structure(self, chunks: List[StoryChunk]) -> Dict:
        """Analyze three-act structure distribution"""
        
        total_chunks = len(chunks)
        if total_chunks == 0:
            return {'act1': 0, 'act2': 0, 'act3': 0}
        
        # Ideal distribution: Act 1 (25%), Act 2 (50%), Act 3 (25%)
        act1_end = total_chunks // 4
        act3_start = total_chunks * 3 // 4
        
        act1_chunks = chunks[:act1_end]
        act2_chunks = chunks[act1_end:act3_start]
        act3_chunks = chunks[act3_start:]
        
        return {
            'act1': len(act1_chunks),
            'act2': len(act2_chunks),
            'act3': len(act3_chunks),
            'balance_score': self.calculate_act_balance(len(act1_chunks), len(act2_chunks), len(act3_chunks))
        }

    def calculate_act_balance(self, act1_len: int, act2_len: int, act3_len: int) -> float:
        """Calculate how well balanced the three acts are"""
        total = act1_len + act2_len + act3_len
        if total == 0:
            return 0
        
        # Ideal ratios
        ideal_act1 = total * 0.25
        ideal_act2 = total * 0.50
        ideal_act3 = total * 0.25
        
        # Calculate deviation from ideal
        deviation = (abs(act1_len - ideal_act1) + 
                    abs(act2_len - ideal_act2) + 
                    abs(act3_len - ideal_act3)) / total
        
        # Convert to score (lower deviation = higher score)
        balance_score = max(0, 1 - deviation)
        return balance_score * 10  # Scale to 0-10

    def identify_story_beats(self, chunks: List[StoryChunk]) -> Dict:
        """Identify key story beats in the narrative"""
        
        found_beats = {}
        
        # Look for story beats based on content and position
        for i, chunk in enumerate(chunks):
            text_lower = chunk.text.lower()
            position_ratio = i / len(chunks) if len(chunks) > 0 else 0
            
            # Opening image (first 10%)
            if position_ratio < 0.1 and 'opening_image' not in found_beats:
                if any(word in text_lower for word in ['begin', 'start', 'first', 'initially']):
                    found_beats['opening_image'] = chunk.text[:100]
            
            # Inciting incident (10-20%)
            elif 0.1 <= position_ratio < 0.2 and 'inciting_incident' not in found_beats:
                if any(word in text_lower for word in ['suddenly', 'then', 'problem', 'change']):
                    found_beats['inciting_incident'] = chunk.text[:100]
            
            # Plot point 1 (around 25%)
            elif 0.2 <= position_ratio < 0.3 and 'plot_point_1' not in found_beats:
                if chunk.chunk_type in ['conflict', 'setup']:
                    found_beats['plot_point_1'] = chunk.text[:100]
            
            # Midpoint (around 50%)
            elif 0.45 <= position_ratio < 0.55 and 'midpoint' not in found_beats:
                if any(word in text_lower for word in ['realize', 'discover', 'revelation', 'turn']):
                    found_beats['midpoint'] = chunk.text[:100]
            
            # Plot point 2 (around 75%)
            elif 0.7 <= position_ratio < 0.8 and 'plot_point_2' not in found_beats:
                if chunk.chunk_type == 'conflict' or 'crisis' in text_lower:
                    found_beats['plot_point_2'] = chunk.text[:100]
            
            # Climax (80-90%)
            elif 0.8 <= position_ratio < 0.9 and 'climax' not in found_beats:
                if any(word in text_lower for word in ['final', 'climax', 'showdown', 'confrontation']):
                    found_beats['climax'] = chunk.text[:100]
            
            # Resolution (final 10%)
            elif position_ratio >= 0.9 and 'resolution' not in found_beats:
                if chunk.chunk_type == 'resolution' or any(word in text_lower for word in ['end', 'finally', 'conclusion']):
                    found_beats['resolution'] = chunk.text[:100]
        
        return found_beats

    def identify_propp_functions(self, chunks: List[StoryChunk]) -> List[str]:
        """Identify Vladimir Propp's narrative functions"""
        
        found_functions = []
        
        function_keywords = {
            'absentation': ['leave', 'absent', 'go away', 'departure'],
            'interdiction': ['forbid', 'warn', 'must not', 'do not'],
            'violation': ['disobey', 'ignore', 'break', 'violate'],
            'villainy': ['villain', 'evil', 'harm', 'attack', 'steal'],
            'departure': ['journey', 'quest', 'travel', 'set out'],
            'struggle': ['fight', 'battle', 'combat', 'struggle'],
            'victory': ['defeat', 'win', 'victory', 'triumph'],
            'return': ['return', 'come back', 'home'],
            'wedding': ['marry', 'wedding', 'unite', 'together']
        }
        
        for chunk in chunks:
            text_lower = chunk.text.lower()
            for function, keywords in function_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    if function not in found_functions:
                        found_functions.append(function)
        
        return found_functions

    def analyze_character_development(self, chunks: List[StoryChunk], entities: Dict[str, List[str]]) -> float:
        """Analyze character development across the story"""
        
        character_mentions = {}
        character_contexts = {}
        
        # Track character mentions and contexts
        for chunk in chunks:
            for entity in entities.get('names', []):
                if entity.lower() in chunk.text.lower():
                    if entity not in character_mentions:
                        character_mentions[entity] = 0
                        character_contexts[entity] = []
                    
                    character_mentions[entity] += 1
                    character_contexts[entity].append(chunk.chunk_type)
        
        if not character_mentions:
            return 0
        
        # Calculate development score
        development_score = 0
        for character, mentions in character_mentions.items():
            # Characters with more mentions and varied contexts show more development
            context_variety = len(set(character_contexts[character]))
            character_score = min(mentions / 3, 1.0) * context_variety
            development_score += character_score
        
        # Normalize by number of characters
        return min(10, development_score / len(character_mentions))

    def analyze_themes(self, chunks: List[StoryChunk]) -> Dict:
        """Analyze thematic content"""
        
        theme_keywords = {
            'love': ['love', 'romance', 'relationship', 'heart'],
            'death': ['death', 'die', 'kill', 'mortality'],
            'power': ['power', 'control', 'authority', 'dominate'],
            'freedom': ['freedom', 'liberty', 'independence', 'free'],
            'justice': ['justice', 'fair', 'right', 'wrong'],
            'redemption': ['redeem', 'forgive', 'second chance', 'redemption'],
            'sacrifice': ['sacrifice', 'give up', 'loss', 'pay price'],
            'identity': ['identity', 'self', 'who am i', 'become']
        }
        
        theme_scores = {}
        theme_chunks = 0
        
        for chunk in chunks:
            text_lower = chunk.text.lower()
            chunk_themes = 0
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    if theme not in theme_scores:
                        theme_scores[theme] = 0
                    theme_scores[theme] += 1
                    chunk_themes += 1
            
            if chunk_themes > 0:
                theme_chunks += 1
        
        # Calculate depth and subtext scores
        depth_score = min(10, len(theme_scores) * 2)  # More themes = deeper
        subtext_score = min(10, (theme_chunks / len(chunks)) * 10 if chunks else 0)
        
        return {
            'themes_found': theme_scores,
            'depth_score': depth_score,
            'subtext_score': subtext_score
        }

    def analyze_conflicts(self, chunks: List[StoryChunk]) -> Dict:
        """Analyze conflict types and intensity"""
        
        conflict_types = {
            'internal': ['struggle with', 'inner', 'doubt', 'decision', 'torn'],
            'interpersonal': ['argue', 'fight', 'disagree', 'against', 'versus'],
            'societal': ['society', 'system', 'law', 'tradition', 'culture'],
            'supernatural': ['magic', 'ghost', 'supernatural', 'divine', 'curse'],
            'nature': ['storm', 'disaster', 'survival', 'elements', 'wild']
        }
        
        found_conflicts = {}
        transformation_count = 0
        
        for chunk in chunks:
            if chunk.chunk_type == 'conflict':
                text_lower = chunk.text.lower()
                
                for conflict_type, keywords in conflict_types.items():
                    if any(keyword in text_lower for keyword in keywords):
                        if conflict_type not in found_conflicts:
                            found_conflicts[conflict_type] = 0
                        found_conflicts[conflict_type] += 1
                
                # Look for transformation markers
                if any(word in text_lower for word in ['change', 'become', 'transform', 'different']):
                    transformation_count += 1
        
        specificity_score = min(10, len(found_conflicts) * 3)
        
        return {
            'conflicts_found': found_conflicts,
            'specificity_score': specificity_score,
            'transformation_count': transformation_count
        }

    def analyze_emotional_arc(self, chunks: List[StoryChunk]) -> Dict:
        """Analyze the emotional progression through the story"""
        
        emotion_progression = []
        emotion_counts = {}
        
        for chunk in chunks:
            chunk_emotions = chunk.emotions
            emotion_progression.append(chunk_emotions)
            
            for emotion in chunk_emotions:
                if emotion not in emotion_counts:
                    emotion_counts[emotion] = 0
                emotion_counts[emotion] += 1
        
        # Calculate volatility (how much emotions change)
        volatility = 0
        if len(emotion_progression) > 1:
            for i in range(1, len(emotion_progression)):
                prev_emotions = set(emotion_progression[i-1])
                curr_emotions = set(emotion_progression[i])
                change = len(prev_emotions.symmetric_difference(curr_emotions))
                volatility += change
            volatility = volatility / (len(emotion_progression) - 1)
        
        # Get dominant emotions
        dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        dominant_emotions = [emotion for emotion, count in dominant_emotions]
        
        return {
            'progression': emotion_progression,
            'volatility': min(10, volatility * 2),
            'dominant': dominant_emotions
        }

    def process_pdf_content(self, pdf_content: bytes) -> str:
        """Extract text content from PDF"""
        try:
            with pdfplumber.open(pdf_content) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n\n"
                return full_text
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return ""

    def generate_personalized_questions(self, text_content: str, chunks: List[StoryChunk], 
                                      all_entities: Dict[str, List[str]], 
                                      relationships: List[Relationship]) -> List[Dict]:
        """Generate personalized questions based on extracted content"""
        
        questions = []
        
        # Character-based questions
        if all_entities.get('names'):
            main_characters = all_entities['names'][:3]  # Focus on first 3 characters
            for character in main_characters:
                questions.append({
                    'type': 'character',
                    'question': f"What drives {character}'s actions throughout the story?",
                    'focus': character,
                    'reasoning': f"Character analysis for {character}"
                })
        
        # Relationship-based questions
        if relationships:
            strong_relationships = [r for r in relationships if r.strength > 0.5]
            for rel in strong_relationships[:2]:  # Top 2 relationships
                questions.append({
                    'type': 'relationship',
                    'question': f"How does the {rel.relationship_type} relationship between {rel.entity1} and {rel.entity2} evolve?",
                    'focus': f"{rel.entity1}-{rel.entity2}",
                    'reasoning': f"Exploring {rel.relationship_type} relationship dynamics"
                })
        
        # Conflict-based questions
        conflict_chunks = [c for c in chunks if c.chunk_type == 'conflict']
        if conflict_chunks:
            questions.append({
                'type': 'conflict',
                'question': "What is the central conflict and how is it resolved?",
                'focus': 'main_conflict',
                'reasoning': "Analyzing primary story conflict"
            })
        
        # Theme-based questions
        theme_chunks = [c for c in chunks if c.chunk_type == 'theme']
        if theme_chunks:
            questions.append({
                'type': 'theme',
                'question': "What are the main themes and how are they developed?",
                'focus': 'themes',
                'reasoning': "Thematic analysis"
            })
        
        # Location-based questions
        if all_entities.get('locations'):
            main_location = all_entities['locations'][0]
            questions.append({
                'type': 'setting',
                'question': f"How does the setting of {main_location} influence the story?",
                'focus': main_location,
                'reasoning': f"Setting analysis for {main_location}"
            })
        
        # Fallback generic questions if content is limited
        if len(questions) < 3:
            generic_questions = [
                {
                    'type': 'plot',
                    'question': "What are the key plot points that drive the narrative forward?",
                    'focus': 'plot_structure',
                    'reasoning': "Plot structure analysis"
                },
                {
                    'type': 'development',
                    'question': "How do the characters change throughout the story?",
                    'focus': 'character_development',
                    'reasoning': "Character growth analysis"
                },
                {
                    'type': 'message',
                    'question': "What message or lesson does this story convey?",
                    'focus': 'story_message',
                    'reasoning': "Core message identification"
                }
            ]
            
            for q in generic_questions:
                if len(questions) < 5:
                    questions.append(q)
        
        return questions[:5]  # Return max 5 questions

# Initialize the engine
engine = StoryIntelligenceEngine()

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_deck():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read PDF content
        pdf_content = file.read()
        
        # Extract text from PDF
        text_content = engine.process_pdf_content(pdf_content)
        
        if not text_content or len(text_content.strip()) < 50:
            return jsonify({'error': 'Could not extract meaningful content from PDF'}), 400
        
        # Process the content through our engine
        print(f"Extracted text length: {len(text_content)}")
        print(f"First 200 chars: {text_content[:200]}")
        
        # Extract entities with detailed context
        all_entities = engine.extract_entities_with_context(text_content)
        print(f"Extracted entities: {all_entities}")
        
        # Extract detailed relationships
        relationships = engine.extract_relationships_detailed(text_content, all_entities)
        print(f"Found {len(relationships)} relationships")
        
        # Analyze story chunks
        chunks = engine.analyze_text_chunks(text_content)
        print(f"Created {len(chunks)} story chunks")
        
        # Generate diagnostic
        diagnostic = engine.generate_story_diagnostic(chunks, all_entities)
        print(f"Generated diagnostic with {len(diagnostic)} metrics")
        
        # Generate personalized questions based on content
        questions = engine.generate_personalized_questions(text_content, chunks, all_entities, relationships)
        print(f"Generated {len(questions)} personalized questions")
        
        # Generate conversation ID
        conversation_id = hashlib.md5(text_content.encode()).hexdigest()[:12]
        
        # Prepare response data
        response_data = {
            'conversation_id': conversation_id,
            'questions': questions,
            'diagnostic': diagnostic,
            'entities': all_entities,
            'relationships': [
                {
                    'entity1': r.entity1,
                    'entity2': r.entity2,
                    'type': r.relationship_type,
                    'strength': r.strength,
                    'evidence': r.evidence[:2]  # Limit evidence for response size
                } for r in relationships
            ],
            'chunk_analysis': {
                'total_chunks': len(chunks),
                'chunk_types': {chunk_type: len([c for c in chunks if c.chunk_type == chunk_type]) 
                              for chunk_type in set(c.chunk_type for c in chunks)},
                'high_importance_chunks': len([c for c in chunks if c.importance > 0.7])
            },
            'content_preview': text_content[:500] + "..." if len(text_content) > 500 else text_content
        }
        
        print(f"Sending response with {len(questions)} questions")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in upload_deck: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # For now, return a simple response
        # Later this will integrate with OpenAI for dynamic responses
        response = {
            'response': f"I understand you're asking: '{message}'. This is where I would provide a thoughtful analysis based on your uploaded story content.",
            'conversation_id': conversation_id
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
