import spacy
from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer
from typing import Dict, List
import numpy as np
from collections import Counter

class AdvancedStoryAnalyzer:
    def __init__(self, supabase_client):
        self.nlp = spacy.load("en_core_web_lg")  # Need large model
        self.documentary_analyzer = DocumentaryStyleAnalyzer()
        self.supabase = supabase_client
        
    def detect_narrative_voice(self, doc) -> Dict:
        """Detect who's speaking and how"""
        
        # First person indicators (filmmaker present)
        first_person = len([t for t in doc if t.text.lower() in ['i', 'we', 'my', 'our']])
        
        # Second person (addressing audience directly)
        second_person = len([t for t in doc if t.text.lower() in ['you', 'your']])
        
        # Passive vs active voice
        passive_sentences = 0
        active_sentences = 0
        for sent in doc.sents:
            if any(token.dep_ == "nsubjpass" for token in sent):
                passive_sentences += 1
            else:
                active_sentences += 1
        
        # Authoritative language patterns
        authority_patterns = ['must', 'should', 'clearly', 'obviously', 'certainly', 'proves']
        authority_score = sum(1 for token in doc if token.text.lower() in authority_patterns)
        
        return {
            'perspective': 'first_person' if first_person > 5 else 'third_person',
            'audience_address': second_person > 0,
            'voice_authority': authority_score / len(doc) * 100,
            'passive_ratio': passive_sentences / (passive_sentences + active_sentences)
        }
    
    def detect_argument_structure(self, doc) -> Dict:
        """Identify if making argument vs observing"""
        
        # Claim-evidence patterns
        claim_markers = ['therefore', 'thus', 'hence', 'proves', 'demonstrates', 'shows that']
        evidence_markers = ['according to', 'research shows', 'data indicates', 'evidence suggests']
        
        has_claims = any(marker in doc.text.lower() for marker in claim_markers)
        has_evidence = any(marker in doc.text.lower() for marker in evidence_markers)
        
        # Causal reasoning
        causal_deps = []
        for token in doc:
            if token.dep_ in ["advcl", "ccomp"] and token.head.pos_ == "VERB":
                for child in token.children:
                    if child.text.lower() in ['because', 'since', 'as']:
                        causal_deps.append((token.head.text, token.text))
        
        return {
            'argument_present': has_claims and has_evidence,
            'causal_chains': len(causal_deps),
            'reasoning_type': 'deductive' if has_claims else 'inductive'
        }
    
    def detect_filmmaker_presence(self, text: str) -> str:
        """Determine filmmaker's role in narrative"""
        
        doc = self.nlp(text)
        
        interview_markers = ['interview', 'asked', 'told me', 'said to me', 'conversation with']
        observation_markers = ['watched', 'observed', 'followed', 'documented', 'captured']
        intervention_markers = ['i confronted', 'i challenged', 'i asked', 'my investigation']
        
        interview_count = sum(1 for marker in interview_markers if marker in text.lower())
        observation_count = sum(1 for marker in observation_markers if marker in text.lower())
        intervention_count = sum(1 for marker in intervention_markers if marker in text.lower())
        
        if intervention_count > 2:
            return 'participatory'
        elif interview_count > observation_count:
            return 'participatory'
        elif observation_count > 0 and interview_count == 0:
            return 'observational'
        else:
            voice = self.detect_narrative_voice(doc)
            if voice['voice_authority'] > 5:
                return 'expository'
            return 'unknown'
    
    def analyze_story_structure(self, doc) -> Dict:
        """Deep structural analysis using dependency parsing"""
        
        # Extract narrative sequences using dependency chains
        event_chains = []
        for sent in doc.sents:
            # Find main verb
            root = [token for token in sent if token.dep_ == "ROOT"][0] if any(token.dep_ == "ROOT" for token in sent) else None
            if root and root.pos_ == "VERB":
                # Get subject and object
                subj = [child for child in root.children if "subj" in child.dep_]
                obj = [child for child in root.children if "obj" in child.dep_]
                if subj:
                    event_chains.append({
                        'actor': subj[0].text,
                        'action': root.text,
                        'object': obj[0].text if obj else None,
                        'tense': root.tag_
                    })
        
        # Detect temporal progression
        past_events = [e for e in event_chains if 'VBD' in e.get('tense', '')]
        present_events = [e for e in event_chains if 'VBZ' in e.get('tense', '') or 'VBP' in e.get('tense', '')]
        
        # Identify turning points (adversative conjunctions)
        turning_points = []
        for sent in doc.sents:
            if any(token.text.lower() in ['but', 'however', 'yet', 'although'] for token in sent):
                turning_points.append(sent.text)
        
        return {
            'event_chains': event_chains[:10],
            'temporal_structure': 'chronological' if len(past_events) > len(present_events) else 'mixed',
            'turning_points': turning_points,
            'has_progression': len(event_chains) > 3
        }
    
    def analyze_deck(self, raw_text: str) -> Dict:
        """Analyze deck using sophisticated NLP + documentary theory"""
        doc = self.nlp(raw_text)
        
        # USE THE SOPHISTICATED ANALYZER
        documentary_analysis = self.documentary_analyzer.analyze_pitch(raw_text)
        
        # Your existing analysis
        mode = self.detect_filmmaker_presence(raw_text)
        voice = self.detect_narrative_voice(doc)
        argument = self.detect_argument_structure(doc)
        structure = self.analyze_story_structure(doc)
        
        # Extract entities
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        # Custom extraction for Characters section
        import re
        characters_match = re.search(r'(?i)characters?:(.*?)(?:\n\n|\Z)', raw_text, re.DOTALL)
        if characters_match:
            characters_text = characters_match.group(1)
            # Extract names from bullet points (- Name: description)
            character_pattern = r'[-•]\s*([^:]+?):\s*[^\n]+'
            found_characters = re.findall(character_pattern, characters_text)
            # Clean and add to people list
            for name in found_characters:
                clean_name = name.strip()
                if clean_name and clean_name not in people:
                    people.append(clean_name)
        
        # Remove duplicates while preserving order
        people = list(dict.fromkeys(people))
        
        # Use sophisticated mode if detected, fallback to basic
        final_mode = documentary_analysis['dominant_styles'][0] if documentary_analysis['dominant_styles'] else mode
        
        return {
            'documentary_styles': documentary_analysis['dominant_styles'],
            'style_gaps': documentary_analysis['gaps'],
            'production_methods': documentary_analysis.get('production_methods', {}),
            'documentary_mode': final_mode,
            'narrative_voice': voice,
            'argument_structure': argument,
            'story_structure': structure,
            'people': people,
            'locations': locations,
            'raw_text_lower': raw_text.lower()
        }
    
    def generate_questions(self, analysis: Dict) -> List[str]:
        """Generate questions from sophisticated style gaps"""
        questions = []
        
        # Map gaps to questions
        gap_to_question = {
            'no_counterargument_consideration': "How will you address opposing viewpoints?",
            'missing_evidence_strategy': "How will you present evidence to build your case?",
            'insufficient_observation_time': "How long will you spend with your subjects?",
            'unclear_filmmaker_role': "What is your role in this story?",
            'no_relationship_context': "What's your personal connection to this topic?",
            'no_authority_voices': "Which experts will validate your argument?",
            'unclear_access': "How will you gain intimate access to observe?",
            'no_production_method': "Will you use interviews, observation, or both?",
            'complex_production': "How will you balance multiple production methods?"
        }
        
        # Add questions based on detected gaps
        for gap in analysis.get('style_gaps', []):
            gap_type = gap.get('type')
            if gap_type in gap_to_question:
                questions.append(gap_to_question[gap_type])
        
        # Add style-specific questions
        styles = analysis.get('documentary_styles', [])
        if 'ARGUMENT-DRIVEN' in styles:
            questions.append("What's your central thesis?")
        elif 'DISCOVERY-FOCUSED' in styles:
            questions.append("What are you hoping to discover?")
        elif 'ENCOUNTER-BASED' in styles:
            questions.append("How does your perspective shape the story?")
        
        # Fallback if not enough
        if len(questions) < 3:
            questions.extend([
                "What transformation occurs from beginning to end?",
                "Who is your target audience?",
                "What unique access do you have?"
            ])
        
        return questions[:5]

    def generate_sophisticated_questions(self, analysis: Dict) -> List[Dict]:
        """Generate academically-grounded questions"""
        
        questions = []
        
        mode = analysis.get('documentary_mode')
        structure = analysis.get('story_structure', {})
        voice = analysis.get('narrative_voice', {})
        
        if mode == 'expository':
            if voice.get('voice_authority', 0) < 5:
                questions.append({
                    'question': "How will you establish authority on this subject?",
                    'rationale': "Expository mode requires authoritative voice (Nichols, 2001)"
                })
        
        elif mode == 'observational':
            questions.append({
                'question': "How long will you embed with subjects to capture authentic moments?",
                'rationale': "Observational mode requires extended unobtrusive presence"
            })
        
        if not structure.get('has_progression'):
            questions.append({
                'question': "What transformation occurs from beginning to end?",
                'rationale': "McKee emphasizes change as essential to story"
            })
        
        if len(structure.get('turning_points', [])) == 0:
            questions.append({
                'question': "What obstacles or reversals complicate the journey?",
                'rationale': "Progressive complications drive narrative engagement"
            })
        
        return questions
    
    def gather_mode_intentions(self) -> List[str]:
        """Generate questions to determine documentary approach"""
        return [
            "Will you appear on camera? (never/occasionally/frequently)",
            "Who narrates the story? (anonymous narrator/me as filmmaker/subjects tell own story)",
            "How will you present evidence? (to support my argument/as it naturally unfolds/through my investigation)",
            "What's your camera approach? (invisible observer/active participant/analytical tool)"
        ]

    def classify_mode_from_intentions(self, answers: Dict) -> str:
        """Classify based on explicit filmmaker choices"""
        
        on_camera = answers.get('on_camera', '').lower()
        narrator = answers.get('narrator', '').lower()
        evidence = answers.get('evidence', '').lower()
        camera = answers.get('camera', '').lower()
        
        if 'never' in on_camera and 'invisible' in camera:
            return 'observational'
        elif 'frequently' in on_camera and 'participant' in camera:
            return 'participatory'
        elif 'anonymous narrator' in narrator and 'support my argument' in evidence:
            return 'expository'
        elif 'me as filmmaker' in narrator and 'my investigation' in evidence:
            return 'performative'
        else:
            return 'hybrid'

    def generate_suggestions(self, analysis: Dict, answers: List[Dict]) -> List[Dict]:
        """Generate actionable suggestions based on analysis and answers"""
        suggestions = []
        
        # First, check if we can determine mode from intention answers
        mode_answers = {}
        for qa in answers:
            if 'appear on camera' in qa['question'].lower():
                mode_answers['on_camera'] = qa['answer']
            if 'narrates' in qa['question'].lower():
                mode_answers['narrator'] = qa['answer']
            if 'present evidence' in qa['question'].lower():
                mode_answers['evidence'] = qa['answer']
            if 'camera approach' in qa['question'].lower():
                mode_answers['camera'] = qa['answer']
        
        # If we have mode answers, classify and provide specific guidance
        if mode_answers:
            inferred_mode = self.classify_mode_from_intentions(mode_answers)
            if inferred_mode == 'observational':
                suggestions.append({
                    'area': 'Documentary Approach',
                    'issue': 'Observational mode identified',
                    'suggestion': 'Your choice to stay off-camera with subjects telling their own story suggests observational mode. Plan for: long embedding periods, patient waiting for moments, minimal crew presence.',
                    'framework': 'Nichols: Observational mode requires unobtrusive presence'
                })
            elif inferred_mode == 'participatory':
                suggestions.append({
                    'area': 'Documentary Approach', 
                    'issue': 'Participatory mode identified',
                    'suggestion': 'Your on-camera presence suggests participatory mode. Plan how your interactions will drive narrative forward.',
                    'framework': 'Nichols: Participatory mode uses filmmaker-subject dynamic as narrative engine'
                })
        
        # Check specific answers for gaps
        for qa in answers:
            answer = qa['answer'].lower()
            question = qa['question']
            
            if 'access' in question.lower() or 'materials' in question.lower():
                if 'exclusive' not in answer and 'never before' not in answer:
                    suggestions.append({
                        'area': 'Access',
                        'issue': 'Not sufficiently exclusive',
                        'suggestion': 'Specify what makes your access unique. Name specific documents, footage, or relationships that competitors cannot replicate.',
                        'example': 'Instead of "interviews with family" say "exclusive first-time interviews with the victim\'s children who have never spoken publicly"'
                    })
            
            if 'transformation' in question.lower() or 'change' in question.lower():
                if not self._detects_change(answer):
                    suggestions.append({
                        'area': 'Story Arc',
                        'issue': 'No clear transformation',
                        'suggestion': 'Describe how your subject/situation changes from beginning to end. What do they believe at start vs end?',
                        'framework': 'McKee: Story is change - your protagonist must transform through conflict'
                    })
            
            if 'obstacles' in question.lower() or 'complications' in question.lower():
                if not self._detects_conflict(answer):
                    suggestions.append({
                        'area': 'Dramatic Tension',
                        'issue': 'Insufficient conflict',
                        'suggestion': 'Identify specific obstacles that prevent easy resolution. What forces oppose your protagonist?',
                        'framework': 'Progressive complications escalate tension toward crisis'
                    })
        
        # Add suggestions based on original analysis gaps only if mode wasn't determined
        if analysis.get('documentary_mode') == 'unknown' and not mode_answers:
            suggestions.append({
                'area': 'Approach',
                'issue': 'Unclear documentary approach',
                'suggestion': 'Clarify your role: Will you observe (fly on wall), participate (on camera), or investigate (following evidence)?',
                'framework': 'Nichols: Mode determines your production method and audience expectations'
            })
        
        if not analysis.get('story_structure', {}).get('has_progression'):
            suggestions.append({
                'area': 'Narrative Structure',
                'issue': 'Lacks clear progression',
                'suggestion': 'Map out beginning, middle, and end. What changes between these points?',
                'framework': 'Three-act structure provides narrative satisfaction'
            })
        
        return suggestions

    def _detects_change(self, text: str) -> bool:
        """Check if answer describes transformation"""
        change_words = ['becomes', 'transforms', 'realizes', 'discovers', 'changes', 'evolves', 'learns']
        return any(word in text for word in change_words)
    
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
            ('discovery-focused', 'todorov'): {
                'tension': "You're discovering but planning for a neat ending",
                'opportunity': "What if discovery leads somewhere unexpected?",
                'choices': ["Follow discovery wherever it goes", "Use structure as a guide", "Make the tension your method"]
            },
            ('argument-driven', 'processual'): {
                'tension': "You're making a point but just following along",
                'opportunity': "The gap between thesis and reality could be powerful",
                'choices': ["Let your point emerge from events", "Use ongoing events as evidence", "Question your own argument"]
            },
            ('encounter-based', 'circular'): {
                'tension': "Personal encounters but returning to start",
                'opportunity': "The return could reveal how encounters changed you",
                'choices': ["Show transformation through encounters", "Use circularity to highlight personal growth", "Question if you can truly return"]
            }
        }
        
        # Convert style to match tension_map keys (handle both formats)
        style_key = style.lower().replace('_', '-')
        key = (style_key, structure)
        if key in tension_map:
            tensions.append(tension_map[key])
            
        return tensions
    def generate_followup_question(self, original_question: str, user_answer: str, analysis: Dict) -> str:
        """Generate intelligent follow-up based on user's answer"""
        answer_lower = user_answer.lower()
        
        # Conflict-related follow-ups
        if 'stopping' in original_question.lower() or 'conflict' in original_question.lower():
            if 'government' in answer_lower or 'regulation' in answer_lower:
                return "How does this regulatory conflict affect your main character personally?"
            elif 'money' in answer_lower or 'financial' in answer_lower:
                return "What specific financial pressure creates the most dramatic tension?"
            elif 'family' in answer_lower or 'personal' in answer_lower:
                return "What moment will show this family conflict most powerfully on screen?"
            else:
                return "Can you get access to film this conflict as it happens?"
        
        # Transformation follow-ups  
        elif 'changes' in original_question.lower() or 'transform' in original_question.lower():
            if 'loses' in answer_lower or 'destroyed' in answer_lower:
                return "What does your character do when they realize what they've lost?"
            elif 'learns' in answer_lower or 'realizes' in answer_lower:
                return "What specific moment shows them having this realization?"
            else:
                return "How will the audience see this change happening?"
        
        # Stakes follow-ups
        elif 'care' in original_question.lower() or 'matter' in original_question.lower():
            if 'environment' in answer_lower or 'climate' in answer_lower:
                return "What makes this environmental story different from others we've seen?"
            elif 'community' in answer_lower or 'tradition' in answer_lower:
                return "Who else is fighting to preserve this tradition?"
            else:
                return "What happens if your character fails?"
        
        # Generic follow-up if no specific pattern matches
        return "That's interesting - can you give me a specific example of how this plays out?"
