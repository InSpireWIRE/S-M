import re
import spacy
from typing import List, Dict, Tuple, Optional
from collections import Counter

class UniversalDocumentaryChunker:
    """Adaptive chunking for any documentary pitch deck structure"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            self.nlp = spacy.load("en_core_web_sm")
        
        # Core elements EVERY documentary pitch needs (regardless of structure)
        self.core_elements = {
            'story': {
                'patterns': [r'(?i)(story|narrative|what happened|incident|event|crime|investigation)'],
                'keywords': ['happened', 'occurred', 'discovered', 'found', 'began', 'started'],
                'priority': 1
            },
            'subjects': {
                'patterns': [r'(?i)(subject|character|protagonist|victim|perpetrator|killer|hero|person)'],
                'keywords': ['who', 'person', 'individual', 'victim', 'suspect'],
                'priority': 1
            },
            'access': {
                'patterns': [r'(?i)(access|exclusive|footage|archive|interview|material|source)'],
                'keywords': ['exclusive', 'never before', 'unprecedented', 'unique', 'rare'],
                'priority': 1
            },
            'stakes': {
                'patterns': [r'(?i)(stakes|why.*matter|importance|consequence|impact|relevance)'],
                'keywords': ['at stake', 'matters', 'important', 'consequences', 'impact'],
                'priority': 2
            },
            'approach': {
                'patterns': [r'(?i)(style|tone|approach|visual|look|format|structure)'],
                'keywords': ['style', 'tone', 'visual', 'cinematic', 'format'],
                'priority': 2
            },
            'credibility': {
                'patterns': [r'(?i)(production|company|producer|director|team|credit|experience)'],
                'keywords': ['produced', 'directed', 'award', 'Emmy', 'Oscar', 'experience'],
                'priority': 3
            }
        }
        
        # Genre-specific patterns
        self.genre_patterns = {
            'true_crime': {
                'indicators': ['murder', 'kill', 'crime', 'investigation', 'detective', 'victim', 'suspect'],
                'expected_elements': ['crime_description', 'perpetrators', 'victims', 'investigation', 'resolution']
            },
            'character_study': {
                'indicators': ['portrait', 'profile', 'life of', 'story of', 'journey', 'transformation'],
                'expected_elements': ['subject_background', 'conflict', 'transformation', 'current_status']
            },
            'investigative': {
                'indicators': ['uncover', 'expose', 'reveal', 'truth', 'investigation', 'scandal'],
                'expected_elements': ['mystery', 'investigation_process', 'findings', 'implications']
            },
            'observational': {
                'indicators': ['follow', 'observe', 'year in', 'process', 'behind the scenes'],
                'expected_elements': ['subject', 'time_period', 'access', 'anticipated_events']
            },
            'historical': {
                'indicators': ['history', 'archive', 'past', 'historical', 'footage', 'retrospective'],
                'expected_elements': ['historical_context', 'archival_materials', 'modern_relevance']
            },
            'social_issue': {
                'indicators': ['issue', 'problem', 'crisis', 'movement', 'change', 'activism'],
                'expected_elements': ['issue_description', 'affected_people', 'proposed_solutions', 'call_to_action']
            }
        }
    
    def process_deck(self, deck_id: str, raw_text: str, file_type: str) -> Dict:
        """Main processing pipeline"""
        
        # Step 1: Clean text (handle OCR issues like in Bad Grandma)
        cleaned_text = self._clean_text(raw_text)
        
        # Step 2: Detect deck structure and genre
        deck_analysis = self._analyze_deck_structure(cleaned_text)
        
        # Step 3: Extract sections using appropriate method
        if deck_analysis['has_clear_sections']:
            raw_chunks = self._extract_marked_sections(cleaned_text, deck_analysis['section_markers'])
        elif deck_analysis['has_episodes']:
            raw_chunks = self._extract_episodes(cleaned_text)
        else:
            raw_chunks = self._extract_semantic_sections(cleaned_text)
        
        # Step 4: Classify and enhance chunks
        classified_chunks = self._classify_chunks(raw_chunks, deck_analysis)
        
        # Step 5: Identify missing elements
        missing_elements = self._identify_gaps(classified_chunks, deck_analysis['genre'])
        
        # Step 6: Store chunks
        stored_chunks = self._store_chunks(deck_id, classified_chunks)
        
        return {
            'deck_id': deck_id,
            'genre': deck_analysis['genre'],
            'structure_type': deck_analysis['structure_type'],
            'total_chunks': len(stored_chunks),
            'elements_found': self._summarize_elements(classified_chunks),
            'missing_elements': missing_elements,
            'chunks': stored_chunks
        }
    
    def _clean_text(self, raw_text: str) -> str:
        """Clean OCR issues and formatting problems"""
        
        # Fix common OCR issues
        text = raw_text.replace('·', '')  # Remove dots used as bullets
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'(\w+)\s*-\s*\n\s*(\w+)', r'\1\2', text)  # Fix broken words
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Fix merged words
        
        # Fix broken sentences
        text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
        
        return text
    
    def _analyze_deck_structure(self, text: str) -> Dict:
        """Comprehensive deck analysis"""
        
        analysis = {
            'genre': 'unknown',
            'structure_type': 'unknown',
            'has_clear_sections': False,
            'has_episodes': False,
            'section_markers': [],
            'detected_elements': {},
            'narrative_style': None
        }
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Detect genre
        genre_scores = {}
        for genre, config in self.genre_patterns.items():
            score = sum(1 for indicator in config['indicators'] if indicator in text_lower)
            genre_scores[genre] = score
        
        if genre_scores:
            analysis['genre'] = max(genre_scores, key=genre_scores.get)
        
        # Detect structure type
        
        # Type 1: Clear sections like TC Squirrel
        clear_headers = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # All caps headers (like "THE RAID", "FORMAT & ACCESS")
            if line_clean and line_clean.isupper() and 3 < len(line_clean) < 100:
                clear_headers.append((i, line_clean))
            # Headers with clear patterns
            elif re.match(r'^(EPISODE|CHAPTER|PART|ACT)\s+\d+', line_clean, re.IGNORECASE):
                clear_headers.append((i, line_clean))
        
        if len(clear_headers) >= 2:
            analysis['has_clear_sections'] = True
            analysis['section_markers'] = clear_headers
            analysis['structure_type'] = 'sectioned'
        
        # Type 2: Episodic structure
        if re.search(r'(?i)(episode\s+\d+|ep\.\s*\d+|chapter\s+\d+)', text):
            analysis['has_episodes'] = True
            analysis['structure_type'] = 'episodic'
        
        # Type 3: Character profiles like Bad Grandma
        if re.search(r'(?i)(THE\s+(KILLERS?|VICTIMS?|SUBJECTS?|CHARACTERS?))', text):
            analysis['structure_type'] = 'character_based'
        
        # Type 4: Narrative flow (no clear sections)
        if not analysis['has_clear_sections'] and not analysis['has_episodes']:
            analysis['structure_type'] = 'narrative_flow'
        
        # Detect narrative style
        first_person_count = len(re.findall(r'\b(I|we|our|my)\b', text[:1000]))
        if first_person_count > 5:
            analysis['narrative_style'] = 'personal'
        elif 'observe' in text_lower or 'follow' in text_lower:
            analysis['narrative_style'] = 'observational'
        else:
            analysis['narrative_style'] = 'expository'
        
        return analysis
    
    def _extract_marked_sections(self, text: str, markers: List[Tuple]) -> List[Dict]:
        """Extract sections with clear headers (TC Squirrel style)"""
        
        chunks = []
        lines = text.split('\n')
        
        for i, (line_num, header) in enumerate(markers):
            # Find section end
            if i < len(markers) - 1:
                next_line = markers[i + 1][0]
            else:
                next_line = len(lines)
            
            content = '\n'.join(lines[line_num:next_line]).strip()
            
            chunks.append({
                'header': header,
                'content': content,
                'type': 'marked_section',
                'position': i
            })
        
        return chunks
    
    def _extract_episodes(self, text: str) -> List[Dict]:
        """Extract episodic content"""
        
        chunks = []
        
        # Split by episode markers
        episode_splits = re.split(r'(?i)((?:EPISODE|EP\.|CHAPTER|PART)\s*\d+[:\s])', text)
        
        current_episode = None
        for part in episode_splits:
            if re.match(r'(?i)(?:EPISODE|EP\.|CHAPTER|PART)\s*\d+', part):
                current_episode = part.strip()
            elif current_episode and part.strip():
                chunks.append({
                    'header': current_episode,
                    'content': part.strip(),
                    'type': 'episode',
                    'position': len(chunks)
                })
        
        return chunks
    
    def _extract_semantic_sections(self, text: str) -> List[Dict]:
        """Extract sections based on semantic content (Bad Grandma style)"""
        
        chunks = []
        doc = self.nlp(text)
        
        # Look for natural breaks
        current_section = {
            'content': [],
            'entities': set(),
            'topics': []
        }
        
        for sent in doc.sents:
            sent_entities = set([ent.text for ent in sent.ents])
            
            # Check for topic shift
            if current_section['entities']:
                overlap = sent_entities.intersection(current_section['entities'])
                
                # If low overlap and we have enough content, start new section
                if len(overlap) < len(sent_entities) * 0.3 and len(current_section['content']) >= 3:
                    # Save current section
                    chunks.append({
                        'header': self._generate_header(current_section),
                        'content': ' '.join(current_section['content']),
                        'type': 'semantic',
                        'position': len(chunks)
                    })
                    
                    # Start new section
                    current_section = {
                        'content': [sent.text],
                        'entities': sent_entities,
                        'topics': []
                    }
                else:
                    current_section['content'].append(sent.text)
                    current_section['entities'].update(sent_entities)
            else:
                current_section['content'].append(sent.text)
                current_section['entities'] = sent_entities
        
        # Don't forget last section
        if current_section['content']:
            chunks.append({
                'header': self._generate_header(current_section),
                'content': ' '.join(current_section['content']),
                'type': 'semantic',
                'position': len(chunks)
            })
        
        return chunks
    
    def _classify_chunks(self, raw_chunks: List[Dict], deck_analysis: Dict) -> List[Dict]:
        """Classify what each chunk represents"""
        
        classified = []
        
        for chunk in raw_chunks:
            chunk_class = self._identify_chunk_purpose(
                chunk['content'], 
                chunk.get('header', ''),
                deck_analysis['genre']
            )
            
            # Extract key information
            doc = self.nlp(chunk['content'][:1000])  # Analyze first 1000 chars
            
            classified.append({
                'deck_id': None,  # Will be set when storing
                'chunk_type': chunk_class['type'],
                'chunk_subtype': chunk_class['subtype'],
                'chunk_number': chunk['position'] + 1,
                'chunk_label': chunk.get('header', chunk_class['suggested_label']),
                'content': chunk['content'],
                'metadata': {
                    'detected_elements': chunk_class['elements_found'],
                    'people': [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
                    'locations': [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]],
                    'dates': [ent.text for ent in doc.ents if ent.label_ == "DATE"],
                    'word_count': len(chunk['content'].split()),
                    'importance_score': chunk_class['importance']
                }
            })
        
        return classified
    
    def _identify_chunk_purpose(self, content: str, header: str, genre: str) -> Dict:
        """Determine what purpose this chunk serves"""
        
        content_lower = content.lower()[:500]
        header_lower = header.lower()
        
        result = {
            'type': 'unknown',
            'subtype': None,
            'elements_found': [],
            'importance': 0.5,
            'suggested_label': 'Section'
        }
        
        # Check against core elements
        for element, config in self.core_elements.items():
            for pattern in config['patterns']:
                if re.search(pattern, header_lower) or re.search(pattern, content_lower):
                    result['elements_found'].append(element)
                    result['importance'] = max(result['importance'], 1.0 / config['priority'])
        
        # Specific classifications based on content
        
        # Opening/Hook
        if any(word in content_lower for word in ['raid', 'incident', 'discovered', 'happened']):
            result['type'] = 'narrative'
            result['subtype'] = 'opening_incident'
            result['suggested_label'] = 'Opening Incident'
            result['importance'] = 0.9
        
        # Character/Subject profiles
        elif 'year-old' in content_lower or re.search(r'\b(he|she|they)\s+(is|was|were)\b', content_lower):
            result['type'] = 'subject'
            result['subtype'] = 'profile'
            result['suggested_label'] = 'Subject Profile'
            result['importance'] = 0.8
        
        # Access/Materials
        elif any(word in content_lower for word in ['exclusive', 'access', 'footage', 'interview']):
            result['type'] = 'production'
            result['subtype'] = 'access'
            result['suggested_label'] = 'Access & Materials'
            result['importance'] = 0.85
        
        # Style/Approach
        elif any(word in content_lower for word in ['style', 'tone', 'visual', 'cinematic']):
            result['type'] = 'production'
            result['subtype'] = 'style'
            result['suggested_label'] = 'Visual Approach'
            result['importance'] = 0.7
        
        # Company/Credits
        elif any(word in content_lower for word in ['productions', 'produced', 'directed', 'award']):
            result['type'] = 'credibility'
            result['subtype'] = 'company'
            result['suggested_label'] = 'Production Company'
            result['importance'] = 0.6
        
        # Episode/Chapter
        elif re.search(r'(?i)(episode|chapter|part)\s+\d+', header_lower):
            result['type'] = 'structure'
            result['subtype'] = 'episode'
            result['suggested_label'] = header
            result['importance'] = 0.75
        
        # Genre-specific classifications
        if genre == 'true_crime':
            if any(word in content_lower for word in ['kill', 'murder', 'crime']):
                result['type'] = 'narrative'
                result['subtype'] = 'crime_description'
                result['importance'] = 0.95
            elif any(word in content_lower for word in ['perpetrator', 'killer', 'suspect']):
                result['type'] = 'subject'
                result['subtype'] = 'perpetrator'
                result['importance'] = 0.85
        
        return result
    
    def _identify_gaps(self, chunks: List[Dict], genre: str) -> List[Dict]:
        """Identify missing essential elements"""
        
        found_elements = set()
        for chunk in chunks:
            found_elements.update(chunk['metadata']['detected_elements'])
        
        missing = []
        
        # Check core elements
        for element, config in self.core_elements.items():
            if element not in found_elements and config['priority'] == 1:
                missing.append({
                    'element': element,
                    'description': f"Missing {element}: No clear {element} section found",
                    'importance': 'critical'
                })
        
        # Check genre-specific requirements
        if genre in self.genre_patterns:
            expected = self.genre_patterns[genre]['expected_elements']
            chunk_types = [c['chunk_subtype'] for c in chunks if c['chunk_subtype']]
            
            for expected_element in expected:
                if expected_element not in chunk_types:
                    missing.append({
                        'element': expected_element,
                        'description': f"For {genre} docs, need clear {expected_element.replace('_', ' ')}",
                        'importance': 'recommended'
                    })
        
        return missing
    
    def _generate_header(self, section_data: Dict) -> str:
        """Generate a header for sections without clear titles"""
        
        if section_data['entities']:
            # Use most prominent entity
            return f"Section: {list(section_data['entities'])[0]}"
        else:
            return f"Section {len(section_data['content'])} sentences"
    
    def _summarize_elements(self, chunks: List[Dict]) -> Dict:
        """Summarize what elements were found"""
        
        summary = {
            'narrative_sections': 0,
            'subject_profiles': 0,
            'production_details': 0,
            'has_episodes': False,
            'has_access_info': False,
            'has_style_guide': False,
            'total_people': set(),
            'total_locations': set()
        }
        
        for chunk in chunks:
            if chunk['chunk_type'] == 'narrative':
                summary['narrative_sections'] += 1
            elif chunk['chunk_type'] == 'subject':
                summary['subject_profiles'] += 1
            elif chunk['chunk_type'] == 'production':
                summary['production_details'] += 1
            
            if chunk['chunk_subtype'] == 'episode':
                summary['has_episodes'] = True
            elif chunk['chunk_subtype'] == 'access':
                summary['has_access_info'] = True
            elif chunk['chunk_subtype'] == 'style':
                summary['has_style_guide'] = True
            
            summary['total_people'].update(chunk['metadata'].get('people', []))
            summary['total_locations'].update(chunk['metadata'].get('locations', []))
        
        summary['total_people'] = list(summary['total_people'])
        summary['total_locations'] = list(summary['total_locations'])
        
        return summary
    
    def _store_chunks(self, deck_id: str, chunks: List[Dict]) -> List[Dict]:
        """Store chunks in database"""
        
        # Clear existing chunks
        self.supabase.table('deck_chunks').delete().eq('deck_id', deck_id).execute()
        
        stored = []
        for chunk in chunks:
            chunk['deck_id'] = deck_id
            result = self.supabase.table('deck_chunks').insert(chunk).execute()
            if result.data:
                stored.append(result.data[0])
        
        return stored
