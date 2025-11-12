import os
import re
import json
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
import hashlib
from typing import List, Dict, Tuple
from dataclasses import dataclass
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from supabase import create_client, Client
import pdfplumber

app = Flask(__name__, template_folder="templates")
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

url = os.environ.get("SUPABASE_URL", "https://cfvjgyysjxgjmnwxzgrk.supabase.co")
key = os.environ.get("SUPABASE_KEY")
key = "sb_publishable_0K-bNGkZJiBsSMS__3AG8w_j5n-UeaX"
supabase: Client = create_client(url, key)

# Initialize OpenAI
# Old api_key line removed

# Story-focused personality configurations for sophisticated documentary development
STORY_PERSONALITIES = {
    'structuralist': {
        'focus': 'hidden narrative architecture',
        'approach': 'investigative_not_prescriptive',
        'core_prompt': """You help filmmakers discover structural patterns they might not have seen. 
                         You ASK if patterns exist, not TELL them what patterns are there. 
                         Use exploratory language: 'Could there be...', 'What if...', 'Do you see...'""",
        'question_starters': ['Could there be', 'What if', 'Do you see', 'Might the structure'],
    },
    
    'subtext_reader': {
        'focus': 'unspoken narrative layers',
        'approach': 'exploratory_not_diagnostic',
        'core_prompt': """You help filmmakers notice gaps and silences that might be meaningful. 
                         You EXPLORE absences, not DECLARE them as answers.
                         Use exploratory language: 'Is there...', 'Might the gap...', 'Could silence...'""",
        'question_starters': ['Is there', 'Might the gap', 'Could silence', 'Do interviews avoid'],
    },
    
    'pattern_recognizer': {
        'focus': 'systemic story connections',
        'approach': 'connective_not_reductive',
        'core_prompt': """You help filmmakers see potential patterns across scales and generations. 
                         You SUGGEST connections, not IMPOSE frameworks.
                         Use exploratory language: 'Do you notice...', 'Could these connect...', 'Might patterns...'""",
        'question_starters': ['Do you notice', 'Could these connect', 'Might patterns', 'Are there echoes'],
    },
    
    'emotional_archaeologist': {
        'focus': 'buried emotional truth',
        'approach': 'revealing_not_interpreting',
        'core_prompt': """You help filmmakers locate authentic emotion beneath surface narrative. 
                         You UNCOVER possibilities, not PSYCHOANALYZE.
                         Use exploratory language: 'Beneath X, might there be...', 'Could the emotion...', 'What if the feeling...'""",
        'question_starters': ['Beneath', 'Could the emotion', 'What if the feeling', 'Might there be'],
    }
}

def select_story_personality(diagnostic):
    """
    Selects based on what might most expand the filmmaker's vision
    Not what's weakest, but what's most fertile for exploration
    """
    if diagnostic['structural_clarity'] > 7 and diagnostic['subtext_density'] < 5:
        return 'subtext_reader'  # Strong structure, explore depths
    elif diagnostic['emotional_archaeology'] < 5:
        return 'emotional_archaeologist'  # Find the feeling
    elif diagnostic['pattern_recognition'] < 5:
        return 'pattern_recognizer'  # Connect the dots
    else:
        return 'structuralist'  # Clarify the architecture

@dataclass
class Chunk:
    text: str
    chunk_type: str
    chunk_subtype: str
    page_numbers: List[int]
    start_char: int
    end_char: int
    entities: Dict
    summary: str = ""
    semantic_score: float = 0.0
    relationships: Dict = None

class DocumentaryChunker:
    """Sophisticated chunking based on documentary story structure"""
    
    # Documentary story markers with subtypes
    STORY_PATTERNS = {
        'synopsis': {
            'patterns': [r'synopsis', r'summary', r'overview', r'logline', r'about', r'introduction', r'premise'],
            'subtypes': ['logline', 'elevator_pitch', 'extended_synopsis']
        },
        'character': {
            'patterns': [r'protagonist', r'character', r'subject', r'profile', r'who', r'main.?person', r'hero'],
            'subtypes': ['protagonist', 'antagonist', 'supporting', 'expert']
        },
        'conflict': {
            'patterns': [r'conflict', r'challenge', r'obstacle', r'problem', r'struggle', r'tension', r'opposition'],
            'subtypes': ['central_conflict', 'internal_conflict', 'external_conflict', 'societal_conflict']
        },
        'stakes': {
            'patterns': [r'stake[s]?', r'risk', r'consequence', r'matter[s]?', r'important', r'at.?stake'],
            'subtypes': ['personal_stakes', 'societal_stakes', 'global_stakes']
        },
        'transformation': {
            'patterns': [r'change', r'transform', r'journey', r'arc', r'evolution', r'growth', r'develop'],
            'subtypes': ['character_arc', 'situational_change', 'revelation']
        },
        'theme': {
            'patterns': [r'theme', r'meaning', r'message', r'explore[s]?', r'examine[s]?', r'deeper', r'universal'],
            'subtypes': ['primary_theme', 'secondary_theme', 'metaphor']
        },
        'evidence': {
            'patterns': [r'footage', r'archive', r'interview', r'document', r'evidence', r'source', r'access'],
            'subtypes': ['archival', 'interviews', 'exclusive_access', 'documents']
        },
        'structure': {
            'patterns': [r'timeline', r'structure', r'act', r'sequence', r'chapter', r'section'],
            'subtypes': ['three_act', 'chronological', 'non_linear', 'parallel']
        }
    }
    
    def __init__(self):
        self.chunks = []
        
    def identify_chunk_type_and_subtype(self, text: str) -> Tuple[str, str]:
        """Identify type and subtype of content"""
        text_lower = text.lower()
        
        best_match = ('general', 'unclassified')
        best_score = 0
        
        for chunk_type, info in self.STORY_PATTERNS.items():
            score = sum(1 for pattern in info['patterns'] 
                       if re.search(pattern, text_lower))
            
            if score > best_score:
                best_score = score
                # Determine subtype based on specific keywords
                subtype = 'general'
                for st in info['subtypes']:
                    if st.replace('_', ' ') in text_lower:
                        subtype = st
                        break
                best_match = (chunk_type, subtype)
        
        return best_match
    
    def extract_entities(self, text: str) -> Dict:
        """Extract named entities, dates, numbers, etc."""
        entities = {
            'names': [],
            'locations': [],
            'organizations': [],
            'dates': [],
            'numbers': [],
            'quotes': [],
            'key_terms': []
        }
        
        # Extract proper nouns (likely names/places)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities['names'] = list(set([n for n in proper_nouns if len(n) > 3]))[:20]
        
        # Extract locations (simple pattern)
        location_patterns = re.findall(r'\b(?:in|at|from|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        entities['locations'] = list(set(location_patterns))[:10]
        
        # Extract organizations
        org_patterns = re.findall(r'\b[A-Z][A-Z]+\b|\b[A-Z][a-z]+\s+(?:Corporation|Company|Institute|Foundation|University|Organization)\b', text)
        entities['organizations'] = list(set(org_patterns))[:10]
        
        # Extract quotes
        quotes = re.findall(r'"([^"]{20,500})"', text)
        entities['quotes'] = quotes[:5]
        
        # Extract dates and years
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        entities['dates'] = list(set(years + dates))[:10]
        
        # Extract numbers and statistics
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', text)
        entities['numbers'] = list(set(numbers))[:10]
        
        # Extract key documentary terms
        key_terms = re.findall(r'\b(?:documentary|film|story|narrative|footage|interview|archive)\b', text.lower())
        entities['key_terms'] = list(set(key_terms))[:10]
        
        return entities
    
    def calculate_semantic_completeness(self, chunk_text: str, chunk_type: str) -> Dict:
        """Calculate how complete this chunk is semantically"""
        completeness = {
            'has_complete_thought': False,
            'has_supporting_details': False,
            'has_conclusion': False,
            'completeness_score': 0.0
        }
        
        sentences = chunk_text.split('. ')
        
        # Check for complete thought (multiple sentences)
        completeness['has_complete_thought'] = len(sentences) > 2
        
        # Check for supporting details (examples, specifics)
        detail_patterns = r'(?:for example|specifically|such as|including|particularly)'
        completeness['has_supporting_details'] = bool(re.search(detail_patterns, chunk_text.lower()))
        
        # Check for conclusion
        conclusion_patterns = r'(?:therefore|thus|in conclusion|ultimately|finally)'
        completeness['has_conclusion'] = bool(re.search(conclusion_patterns, chunk_text.lower()))
        
        # Calculate score
        score = 0.0
        if completeness['has_complete_thought']: score += 0.4
        if completeness['has_supporting_details']: score += 0.3
        if completeness['has_conclusion']: score += 0.3
        
        completeness['completeness_score'] = score
        
        return completeness
    
    def identify_relationships(self, chunks: List[Chunk], current_index: int) -> Dict:
        """Identify relationships between chunks"""
        relationships = {
            'references_previous': [],
            'references_next': [],
            'thematically_related': [],
            'continues_narrative': False
        }
        
        current = chunks[current_index]
        
        # Check for explicit references
        if current_index > 0:
            prev = chunks[current_index - 1]
            # Check if current chunk references previous
            if any(entity in current.text for entity in prev.entities['names'] if entity):
                relationships['references_previous'].append(current_index - 1)
                relationships['continues_narrative'] = True
        
        # Check thematic relationships
        for i, other in enumerate(chunks):
            if i != current_index:
                # Check if same type or related themes
                if other.chunk_type == current.chunk_type:
                    relationships['thematically_related'].append(i)
                # Check for shared entities
                shared_entities = set(current.entities['names']) & set(other.entities['names'])
                if shared_entities:
                    if i not in relationships['thematically_related']:
                        relationships['thematically_related'].append(i)
        
        return relationships
    
    def calculate_narrative_position(self, index: int, total: int) -> Dict:
        """Determine where in the narrative arc this chunk falls"""
        position_ratio = index / max(total - 1, 1)
        
        # Three-act structure
        if position_ratio <= 0.25:
            act = 1
            act_position = "setup"
        elif position_ratio <= 0.5:
            act = 2
            act_position = "rising_action"
        elif position_ratio <= 0.75:
            act = 2
            act_position = "climax"
        else:
            act = 3
            act_position = "resolution"
        
        return {
            'act': act,
            'act_position': act_position,
            'position_ratio': position_ratio,
            'is_beginning': position_ratio < 0.1,
            'is_middle': 0.4 < position_ratio < 0.6,
            'is_end': position_ratio > 0.9
        }
    
    def semantic_chunk(self, text: str, pages_info: List[Tuple[int, str]]) -> List[Chunk]:
        """Intelligently chunk based on semantic structure"""
        chunks = []
        
        # Strategy: Smart sectioning with overlap
        section_markers = re.finditer(
            r'(?:^|\n)([A-Z][A-Z\s]{2,50})(?:\n|$)|(?:^|\n)#{1,3}\s+(.+)(?:\n|$)|(?:^|\n)([A-Z][^.!?]*:)\s*',
            text, re.MULTILINE
        )
        
        sections = []
        last_end = 0
        
        for match in section_markers:
            if match.start() > last_end + 200:  # Minimum section size
                sections.append((last_end, match.start()))
                last_end = match.start()
        sections.append((last_end, len(text)))
        
        # If no clear sections, use sliding window
        if len(sections) <= 2:
            window_size = 5000
            stride = 3500  # 1500 char overlap
            
            position = 0
            while position < len(text):
                end_pos = min(position + window_size, len(text))
                
                # Try to end at paragraph
                chunk_text = text[position:end_pos]
                if end_pos < len(text):
                    last_para = chunk_text.rfind('\n\n')
                    if last_para > window_size * 0.6:
                        chunk_text = chunk_text[:last_para]
                        end_pos = position + last_para
                
                if len(chunk_text.strip()) > 100:
                    sections.append((position, end_pos))
                
                position += stride
                if position >= len(text):
                    break
        
        # Process sections into chunks
        for i, (start, end) in enumerate(sections):
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) < 50:
                continue
            
            # Determine pages this chunk spans
            chunk_pages = self._get_page_numbers(start, end, pages_info)
            
            # Identify type and subtype
            chunk_type, chunk_subtype = self.identify_chunk_type_and_subtype(chunk_text)
            
            # Extract entities
            entities = self.extract_entities(chunk_text)
            
            chunk = Chunk(
                text=chunk_text,
                chunk_type=chunk_type,
                chunk_subtype=chunk_subtype,
                page_numbers=chunk_pages,
                start_char=start,
                end_char=end,
                entities=entities,
                relationships={}  # Will be filled after all chunks are created
            )
            chunks.append(chunk)
        
        # Now calculate relationships between chunks
        for i, chunk in enumerate(chunks):
            chunk.relationships = self.identify_relationships(chunks, i)
        
        return chunks
    
    def _get_page_numbers(self, start_char: int, end_char: int, 
                          pages_info: List[Tuple[int, str]]) -> List[int]:
        """Determine which pages a chunk spans"""
        pages = []
        char_count = 0
        
        for page_num, page_text in pages_info:
            page_start = char_count
            page_end = char_count + len(page_text)
            
            if page_end >= start_char and page_start <= end_char:
                pages.append(page_num)
            
            char_count = page_end
            
        return pages if pages else [1]  # Default to page 1 if no pages found
    
    def generate_story_diagnostic(self, chunks: List[Dict], all_entities: Dict) -> Dict:
        """
        Analyzes the deck's storytelling dimensions
        Returns scores not as judgments but as landscape mapping
        """
        diagnostic = {}
        
        # Structural clarity (0-10)
        act_markers = sum(1 for c in chunks if c.get('narrative_position', {}).get('act_position') in ['setup', 'climax', 'resolution'])
        diagnostic['structural_clarity'] = min(10, act_markers * 3)
        
        # Conflict specificity (0-10)
        conflict_chunks = [c for c in chunks if c.get('chunk_type') == 'conflict']
        conflict_names = sum(len(c.get('metadata', {}).get('entities', {}).get('names', [])) for c in conflict_chunks)
        diagnostic['conflict_specificity'] = min(10, len(conflict_chunks) * 3 + conflict_names)
        
        # Transformation markers (0-10)
        transform_chunks = [c for c in chunks if c.get('chunk_type') == 'transformation']
        change_words = sum(1 for c in chunks if any(word in c.get('content', '').lower() for word in ['change', 'become', 'transform', 'evolve']))
        diagnostic['transformation_markers'] = min(10, len(transform_chunks) * 4 + change_words // 5)
        
        # Thematic depth (0-10)
        theme_chunks = [c for c in chunks if c.get('chunk_type') == 'theme']
        metaphor_indicators = sum(1 for c in chunks if any(word in c.get('content', '').lower() for word in ['represents', 'symbolizes', 'mirrors', 'echoes']))
        diagnostic['thematic_depth'] = min(10, len(theme_chunks) * 3 + metaphor_indicators)
        
        # Perspective diversity (0-10)
        unique_names = len(all_entities.get('names', []))
        quote_count = sum(len(c.get('metadata', {}).get('entities', {}).get('quotes', [])) for c in chunks)
        diagnostic['perspective_diversity'] = min(10, (unique_names // 5) + (quote_count * 2))
        
        # Subtext density (0-10)
        question_marks = sum(c.get('content', '').count('?') for c in chunks)
        uncertainty_words = sum(1 for c in chunks if any(word in c.get('content', '').lower() for word in ['perhaps', 'might', 'could', 'possibly', 'maybe']))
        diagnostic['subtext_density'] = min(10, question_marks + uncertainty_words)
        
        # Pattern recognition (0-10)
        repeated_themes = {}
        for chunk in chunks:
            for name in chunk.get('metadata', {}).get('entities', {}).get('names', []):
                repeated_themes[name] = repeated_themes.get(name, 0) + 1
        patterns_found = sum(1 for count in repeated_themes.values() if count > 2)
        diagnostic['pattern_recognition'] = min(10, patterns_found * 2)
        
        # Emotional archaeology (0-10)
        emotion_words = sum(1 for c in chunks if any(word in c.get('content', '').lower() for word in 
            ['feel', 'felt', 'emotion', 'heart', 'soul', 'fear', 'love', 'hate', 'hope', 'despair']))
        diagnostic['emotional_archaeology'] = min(10, emotion_words // 3)
        
        return diagnostic
    
    def summarize_chunk(self, chunk: Chunk) -> str:
        """Create a focused summary of a chunk"""
        prompt = f"""
        Summarize this {chunk.chunk_type} section from a documentary pitch deck.
        
        Section type: {chunk.chunk_type} ({chunk.chunk_subtype})
        
        Focus on:
        1. Key narrative points
        2. ALL specific names: {', '.join(chunk.entities['names'][:10])}
        3. Important dates: {', '.join(chunk.entities['dates'][:5])}
        4. Central conflict or theme
        
        Content:
        {chunk.text[:6000]}
        
        Provide a dense 3-4 sentence summary preserving all specific details.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Create story-focused summaries for documentary analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback summary
            return f"{chunk.chunk_type.title()} section discussing {', '.join(chunk.entities['names'][:3]) if chunk.entities['names'] else 'the subject'}."

    def extract_story_relationships(self, text: str, entities: Dict) -> Dict:
        """Extract universal story relationships - not just crime"""
        relationships = {
            'power_dynamics': [],
            'emotional_connections': [],
            'transformations': [],
            'conflicts': [],
            'influences': [],
            'dependencies': [],
            'parallels': []
        }
        
        # Power/Authority relationships (works for any documentary)
        power_patterns = [
            r'(\w+)\s+(?:controls?|leads?|directs?|manages?|owns?)',
            r'(\w+)\s+(?:depends on|works for|reports to|follows)',
            r'(\w+)\s+(?:influences?|shapes?|determines?)',
            r'(\w+)\s+(?:resist|challenge|oppose|fight) (?:against\s+)?(\w+)'
        ]
        
        # Emotional/Human connections
        connection_patterns = [
            r'(\w+)\s+(?:loves?|cares? for|supports?|helps?)\s+(\w+)',
            r'(\w+)\s+(?:betrays?|abandons?|leaves?|hurts?)\s+(\w+)',
            r'(\w+)\s+(?:inspired by|motivated by|driven by)\s+(\w+)',
            r'(\w+)\s+(?:fears?|avoids?|escapes? from)\s+(\w+)'
        ]
        
        # Transformation relationships
        transformation_patterns = [
            r'(\w+)\s+(?:becomes?|transforms? into|evolves? into|changes? to)',
            r'(\w+)\s+(?:was|used to be|started as)\s+(.+?)(?:but|before)',
            r'(\w+)\s+(?:discovers?|realizes?|learns?|understands?)'
        ]
        
        # Conflict patterns (broader than crime)
        conflict_patterns = [
            r'(\w+)\s+(?:versus|vs\.?|against|opposes?)\s+(\w+)',
            r'(\w+)\s+(?:struggles? with|battles?|fights?)\s+(.+)',
            r'tension between\s+(\w+)\s+and\s+(\w+)',
            r'(\w+)\s+(?:threatens?|challenges?|undermines?)\s+(\w+)'
        ]
        
        # System/Environmental relationships
        system_patterns = [
            r'(\w+)\s+(?:caused by|results from|stems from)\s+(.+)',
            r'(\w+)\s+(?:leads to|causes?|creates?)\s+(.+)',
            r'(\w+)\s+(?:part of|within|inside)\s+(.+)',
            r'(\w+)\s+(?:reflects?|mirrors?|parallels?)\s+(.+)'
        ]
        
        # Extract each type
        for pattern_list, category in [
            (power_patterns, 'power_dynamics'),
            (connection_patterns, 'emotional_connections'),
            (transformation_patterns, 'transformations'),
            (conflict_patterns, 'conflicts'),
            (system_patterns, 'influences')
        ]:
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                relationships[category].extend(matches)
        
        # Identify protagonist/subject (not victim/perpetrator)
        protagonist_patterns = [
            r'(?:follows?|about|centers? on|focuses? on)\s+(\w+)',
            r'(\w+)(?:\'s|s\')\s+(?:story|journey|life|struggle)',
            r'(?:protagonist|subject|main character|hero)\s+(\w+)'
        ]
        
        relationships['protagonist'] = []
        for pattern in protagonist_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            relationships['protagonist'].extend(matches)
        
        return relationships

    def identify_story_roles(self, chunks_data, all_entities):
        """Identify roles in ANY documentary story"""
        roles = {
            'central_figure': [],      # Who the story follows
            'catalyst': [],            # Who/what triggers change
            'obstacle': [],            # Who/what creates conflict
            'mentor': [],              # Who guides/teaches
            'witness': [],             # Who observes/tells
            'transformed': [],         # Who changes
            'system': [],              # What larger forces are at play
            'community': []            # What groups are involved
        }
        
        for chunk in chunks_data:
            content = chunk.get('content', '').lower()
            
            # Central figure (not just victim/perpetrator)
            if any(word in content for word in ['follows', 'story of', 'journey', 'life of']):
                # Extract the subject of the documentary
                names_in_chunk = [n for n in all_entities.get('names', []) if n.lower() in content]
                roles['central_figure'].extend(names_in_chunk)
            
            # Catalyst (what/who starts the change)
            if any(word in content for word in ['began when', 'started with', 'triggered by']):
                names_in_chunk = [n for n in all_entities.get('names', []) if n.lower() in content]
                roles['catalyst'].extend(names_in_chunk)
            
            # System/Environment
            if any(word in content for word in ['system', 'industry', 'community', 'culture']):
                orgs = [o for o in all_entities.get('organizations', []) if o.lower() in content]
                roles['system'].extend(orgs)
        
        return roles

    def validate_story_understanding(self, question: str, story_roles: Dict) -> tuple:
        """Validate understanding without assuming crime narrative"""
        errors = []
        
        # Check if roles are confused
        central_figures = story_roles.get('central_figure', [])
        obstacles = story_roles.get('obstacle', [])
        
        for figure in central_figures:
            if figure in question:
                # Check if central figure is mischaracterized
                negative_actions = ['manipulates', 'controls', 'orchestrates', 'schemes']
                if any(action in question.lower() for action in negative_actions):
                    # Only an error if this person isn't actually the obstacle
                    if figure not in obstacles:
                        errors.append(f"May mischaracterize {figure}'s role in the story")
        
        # Check for assumed relationships that might not exist
        if 'victim' in question.lower() and 'central_figure' in story_roles:
            if not any(word in question.lower() for word in ['environmental', 'systemic', 'societal']):
                errors.append("Assumes victim narrative when story might be about transformation/discovery")
        
        return len(errors) == 0, errors


@app.route('/api/status')
def home():
    return jsonify({"status": "S!M Backend Running with Sophisticated Chunking"})

def extract_text_with_ocr(file_path, max_pages=10):
    """Fallback to OCR when pdfplumber can't extract text"""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        
        print("No text found, trying OCR extraction...")
        
        # Convert PDF pages to images (limit pages for large files)
        images = convert_from_path(file_path, dpi=150, last_page=min(max_pages, 10))
        
        full_text = ""
        for i, image in enumerate(images):
            print(f"OCR processing page {i+1}")
            text = pytesseract.image_to_string(image)
            full_text += f"\n[Page {i+1}]\n{text}"
        
        return full_text
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""

@app.route('/api/upload-deck', methods=['POST', 'OPTIONS'])
def upload_deck():
    if request.method == 'OPTIONS':
        return '', 200
    
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400
    
    # Extract PDF
    full_text = ""
    pages_info = []
    
    try:
        with pdfplumber.open(file) as pdf:
            total_pages = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                full_text += f"\n[Page {page_num + 1}]\n{page_text}"
                pages_info.append((page_num + 1, page_text))
            
            print(f"DEBUG: full_text length = {len(full_text.strip())}")
            print(f"DEBUG: Check {len(full_text.strip())} < 1000 = {len(full_text.strip()) < 1000}")
            
            # If no text extracted, try OCR
            if len(full_text.strip()) < 1000:
                print("PDFPlumber found no text, trying OCR...")
                temp_path = f"/tmp/{file.filename}"
                file.seek(0)
                file.save(temp_path)
                full_text = extract_text_with_ocr(temp_path, max_pages=10)
                os.remove(temp_path)
                
                # Rebuild pages_info from OCR text
                pages_info = []
                for i in range(min(10, total_pages)):
                    pages_info.append((i + 1, ""))  # Empty for now since OCR gives combined text

            print(f"="*50)
            print(f"PDF EXTRACTION COMPLETE")
            print(f"Filename: {file.filename}")
            print(f"Total pages: {total_pages}")
            print(f"Total characters: {len(full_text)}")
            print(f"="*50)
    
    except Exception as e:
        return jsonify({"error": f"PDF extraction failed: {str(e)}"}), 500
    
    # Initialize chunker
    chunker = DocumentaryChunker()
    chunks = chunker.semantic_chunk(full_text, pages_info)
    
    print(f"Created {len(chunks)} semantic chunks")
    
    # Generate summaries for each chunk
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}: {chunk.chunk_type}/{chunk.chunk_subtype}")
        chunk.summary = chunker.summarize_chunk(chunk)
        chunk.semantic_score = chunker.calculate_semantic_completeness(chunk.text, chunk.chunk_type)
    
    # Create overall summary and extract all entities
    overall_summary_parts = []
    all_entities = {
        'names': set(),
        'locations': set(),
        'organizations': set(),
        'dates': set(),
        'numbers': set()
    }
    
    for chunk in chunks:
        overall_summary_parts.append(f"[{chunk.chunk_type.upper()}] {chunk.summary}")
        for key in ['names', 'locations', 'organizations', 'dates', 'numbers']:
            if key in chunk.entities:
                all_entities[key].update(chunk.entities[key])
    
    overall_summary = "\n\n".join(overall_summary_parts)[:10000]
    
    # Convert sets to lists for JSON serialization
    for key in all_entities:
        all_entities[key] = list(all_entities[key])[:50]
    
    # Extract story relationships using the chunker method
    story_relationships = chunker.extract_story_relationships(full_text, all_entities)
    
    # Store deck in uploaded_decks
    deck_data = {
        'original_filename': file.filename,
        'content_extracted': {
            'text': full_text,
            'pages': total_pages,
            'characters': len(full_text),
            'summary': overall_summary,
            'all_entities': all_entities,
            'story_relationships': story_relationships  # Add relationships to stored data
        },
        'deck_name': file.filename,
        'status': 'analyzed'
    }
    
    deck_result = supabase.table('uploaded_decks').insert(deck_data).execute()
    deck_id = deck_result.data[0]['id']
    
    # Store chunks using YOUR EXISTING SCHEMA
    for i, chunk in enumerate(chunks):
        
        # Calculate metadata for your sophisticated schema
        semantic_completeness = chunker.calculate_semantic_completeness(chunk.text, chunk.chunk_type)
        narrative_position = chunker.calculate_narrative_position(i, len(chunks))
        
        # Get context (previous and next chunks)
        context_before = chunks[i-1].text[:500] if i > 0 else None
        context_after = chunks[i+1].text[:500] if i < len(chunks)-1 else None
        
        chunk_data = {
            'deck_id': deck_id,
            'chunk_type': chunk.chunk_type,
            'chunk_subtype': chunk.chunk_subtype,
            'chunk_number': i,
            'chunk_label': f"{chunk.chunk_type}_{i+1}",
            'content': chunk.text,  # Your column name
            'metadata': {
                'pages': chunk.page_numbers,
                'start_char': chunk.start_char,
                'end_char': chunk.end_char,
                'length': len(chunk.text),
                'summary': chunk.summary,
                'entities': chunk.entities
            },
            'graph_metrics': {
                'entity_count': sum(len(v) for v in chunk.entities.values()),
                'quote_count': len(chunk.entities.get('quotes', [])),
                'name_count': len(chunk.entities.get('names', [])),
                'date_count': len(chunk.entities.get('dates', []))
            },
            'context_before': context_before,
            'context_after': context_after,
            'semantic_completeness': semantic_completeness,
            'relationships': chunk.relationships,
            'narrative_position': narrative_position
        }
        
        supabase.table('deck_chunks').insert(chunk_data).execute()
    
    print(f"Stored {len(chunks)} chunks in database")
    
    return jsonify({
        "deck_id": deck_id,
        "status": "success",
        "message": f"Processed {file.filename}",
        "stats": {
            "pages": total_pages,
            "characters": len(full_text),
            "chunks": len(chunks),
            "chunk_types": dict([(c.chunk_type, sum(1 for ch in chunks if ch.chunk_type == c.chunk_type)) 
                                 for c in chunks]),
            "entities_found": {k: len(v) for k, v in all_entities.items()},
            "relationships_found": {k: len(v) for k, v in story_relationships.items()}
        }
    })

@app.route('/api/start-conversation', methods=['POST', 'OPTIONS'])
def start_conversation():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    deck_id = data.get('deck_id')
    
    # Get deck info
    deck_result = supabase.table('uploaded_decks').select('*').eq('id', deck_id).execute()
    
    # Get all chunks for this deck
    chunks_result = supabase.table('deck_chunks').select('*').eq('deck_id', deck_id).order('chunk_number').execute()
    
    if not chunks_result.data:
        return jsonify({"error": "No chunks found for this deck"}), 400
    
    deck_data = deck_result.data
    chunks_data = chunks_result.data
    
    print(f"="*50)
    print(f"GENERATING QUESTIONS for {deck_data[0]['original_filename']}")
    print(f"Found {len(chunks_data)} chunks")
    
    # Get all entities from deck
    all_entities = deck_data[0]['content_extracted'].get('all_entities', {})
    
    # Initialize chunker to access methods
    chunker = DocumentaryChunker()
    
    # Identify story roles
    story_roles = chunker.identify_story_roles(chunks_data, all_entities)
    
    # Get story relationships if available
    story_relationships = deck_data[0]['content_extracted'].get('story_relationships', {})
    
    # Identify priority chunks for question generation
    priority_chunk_types = ['synopsis', 'character', 'conflict', 'stakes', 'theme', 'transformation']
    priority_chunks = [c for c in chunks_data if c['chunk_type'] in priority_chunk_types]
    
    if not priority_chunks:
        priority_chunks = chunks_data[:5]  # Use first 5 if no priority chunks
    
    # Build context for GPT
    context_parts = []
    chunks_used_ids = []
    
    for chunk in priority_chunks[:6]:  # Use top 6 most relevant chunks
        metadata = chunk.get('metadata', {})
        summary = metadata.get('summary', chunk['content'][:500])
        
        context_parts.append(f"""
        [{chunk['chunk_type'].upper()} - {chunk.get('chunk_subtype', 'general')}]
        {summary}
        Entities: {', '.join(metadata.get('entities', {}).get('names', [])[:5])}
        """)
        
        chunks_used_ids.append(chunk['id'])
    
    context = "\n\n".join(context_parts)
    
    # Identify what's MISSING from the narrative
    found_types = set(c['chunk_type'] for c in chunks_data)
    missing_elements = []
    
    essential_elements = {
        'character': 'WHO is the protagonist/subject',
        'conflict': 'WHAT is the central conflict',
        'stakes': 'WHY does this matter',
        'transformation': 'HOW do things change',
        'evidence': 'WHAT footage/access do you have'
    }
    
    for element, description in essential_elements.items():
        if element not in found_types:
            missing_elements.append(description)
    
    # Generate story diagnostic
    story_diagnostic = chunker.generate_story_diagnostic(chunks_data, all_entities)
    
    # Select personality based on diagnostic
    selected_personality = select_story_personality(story_diagnostic)
    personality_config = STORY_PERSONALITIES[selected_personality]
    
    print(f"Selected personality: {selected_personality}")
    print(f"Diagnostic scores: {story_diagnostic}")
    print(f"Story roles identified: {story_roles}")
    
    # Build sophisticated prompt with exploratory framework
    prompt = f"""
    You are a sophisticated story consultant acting as a {personality_config['focus']} specialist.
    
    APPROACH: {personality_config['approach']}
    
    {personality_config['core_prompt']}
    
    DECK CONTEXT:
    Names found: {', '.join(all_entities.get('names', [])[:20])}
    Locations: {', '.join(all_entities.get('locations', [])[:10])}
    
    STORY ROLES IDENTIFIED:
    Central Figure: {', '.join(story_roles.get('central_figure', [])[:3])}
    Catalyst: {', '.join(story_roles.get('catalyst', [])[:3])}
    System/Environment: {', '.join(story_roles.get('system', [])[:3])}
    
    STORY ELEMENTS PRESENT:
    {context}
    
    DIAGNOSTIC LANDSCAPE (not weaknesses, but territory to explore):
    - Structural clarity: {story_diagnostic['structural_clarity']}/10
    - Conflict specificity: {story_diagnostic['conflict_specificity']}/10  
    - Transformation markers: {story_diagnostic['transformation_markers']}/10
    - Thematic depth: {story_diagnostic['thematic_depth']}/10
    - Emotional archaeology: {story_diagnostic['emotional_archaeology']}/10
    - Pattern recognition: {story_diagnostic['pattern_recognition']}/10
    - Subtext density: {story_diagnostic['subtext_density']}/10
    
    Generate exactly 3 sophisticated questions that:
    
    1. Begin with exploratory language from this list: {personality_config['question_starters']}
    2. Reference SPECIFIC names, places, or events from the deck
    3. Open possibilities rather than prescribe solutions
    4. Respect the filmmaker's authorship
    5. Use "might," "could," "perhaps" not "is," "should," "must"
    6. Help filmmakers discover something they haven't seen, not tell them what their story is
    7. DO NOT assume crime/victim narratives - keep questions universal to any documentary type
    
    Each question should explore different aspects of their material through your {personality_config['focus']} lens.
    
    Return ONLY a JSON array of 3 question strings.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k" if len(prompt) > 3000 else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert documentary story coach. Always reference specific details from the deck."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        questions_text = response.choices[0].message.content
        print(f"GPT Response: {questions_text}")
        
        # Parse questions
        import json
        try:
            if "[" in questions_text and "]" in questions_text:
                start = questions_text.index("[")
                end = questions_text.rindex("]") + 1
                questions = json.loads(questions_text[start:end])
            else:
                questions = json.loads(questions_text)
        except:
            # Fallback parsing
            questions = re.findall(r'"([^"]+\?)"', questions_text)[:3]
            if not questions:
                questions = questions_text.split('\n')[:3]
        
        print(f"Parsed questions: {questions}")
        
        # Validate questions using the chunker method
        for i, question in enumerate(questions):
            valid, errors = chunker.validate_story_understanding(question, story_roles)
            if not valid:
                print(f"Question {i+1} validation errors: {errors}")
        
    except Exception as e:
        print(f"Question generation error: {e}")
        return jsonify({"error": f"Failed to generate questions: {str(e)}"}), 500
    
    # Create conversation
    conv_data = {
        'deck_id': deck_id,
        'status': 'active',
        'current_turn': 1,
        'personality_used': selected_personality,
        'diagnostic_scores': story_diagnostic,
        'story_roles': story_roles  # Store identified roles
    }
    result = supabase.table('conversations').insert(conv_data).execute()
    conversation_id = result.data[0]['id']
    
    print(f"Created conversation: {conversation_id}")
    print(f"="*50)
    
    # Also create the conversation_questions records if that table exists
    try:
        for i, question in enumerate(questions):
            question_data = {
                'conversation_id': conversation_id,
                'question_number': i + 1,
                'question_text': question,
                'chunks_used': chunks_used_ids,
                'entities_referenced': {
                    'names': [n for n in all_entities.get('names', []) if n.lower() in question.lower()],
                    'locations': [l for l in all_entities.get('locations', []) if l.lower() in question.lower()]
                },
                'question_type': ['specific_probe', 'missing_element', 'thematic_depth'][i]
            }
            supabase.table('conversation_questions').insert(question_data).execute()
    except:
        # Table might not exist yet, that's ok
        pass
    
    return jsonify({
        "conversation_id": conversation_id,
        "deck_id": deck_id,
        "questions": questions,
        "analysis": {
            "chunks_analyzed": len(chunks_data),
            "story_elements_found": list(found_types),
            "missing_elements": missing_elements,
            "entities_found": {k: len(v) for k, v in all_entities.items()},
            "story_roles": {k: v[:3] for k, v in story_roles.items() if v}  # Return top 3 of each role
        }
    })

@app.route('/api/submit-answer', methods=['POST', 'OPTIONS'])
def submit_answer():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    conversation_id = data.get('conversation_id')
    question_number = data.get('question_number')
    answer = data.get('answer')
    
    # Store the answer
    answer_data = {
        'conversation_id': conversation_id,
        'question_number': question_number,
        'answer_text': answer
    }
    supabase.table('conversation_answers').insert(answer_data).execute()
    
    # Get conversation context
    conv_result = supabase.table('conversations').select('*').eq('id', conversation_id).single().execute()
    current_turn = conv_result.data['current_turn']
    deck_id = conv_result.data['deck_id']
    story_roles = conv_result.data.get("story_roles", {})
    # Get all previous Q&A for context
    prev_questions = supabase.table('conversation_questions').select('*').eq('conversation_id', conversation_id).order('question_number').execute()
    prev_answers = supabase.table('conversation_answers').select('*').eq('conversation_id', conversation_id).execute()
    
    # Get deck info for context
    deck_result = supabase.table('uploaded_decks').select('*').eq('id', deck_id).single().execute()
    all_entities = deck_result.data['content_extracted'].get('all_entities', {})
    
    # Build conversation history
    conversation_history = []
    for q in prev_questions.data:
        conversation_history.append(f"Q{q['question_number']}: {q['question_text']}")
        # Find matching answer
        for a in prev_answers.data:
            if a['question_number'] == q['question_number']:
                conversation_history.append(f"A{q['question_number']}: {a['answer_text']}")
    
    # Generate FOLLOW-UP question based on the answer
    prompt = f"""
    You are a documentary story coach having a conversation with a filmmaker about their project.
    
    KEY ENTITIES FROM THEIR DECK:
    Names: {', '.join(all_entities.get('names', [])[:10])}
    Locations: {', '.join(all_entities.get('locations', [])[:5])}
    
    STORY ROLES:
    Central Figure: {', '.join(story_roles.get('central_figure', [])[:3])}
    
    CONVERSATION SO FAR:
    {chr(10).join(conversation_history)}
    
    Based on their latest answer, generate a FOLLOW-UP question that:
    1. Digs deeper into what they just revealed
    2. References specific details from their answer
    3. Pushes toward emotional truth and story clarity
    4. Challenges any gaps or inconsistencies
    5. Does NOT assume crime/victim narratives unless explicitly present
    
    This is turn {current_turn} of 5. Make it count.
    
    Generate ONE probing follow-up question.
    """
    
    # Get follow-up question from GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert documentary coach. Build on what they just said, dig deeper."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=150
    )
    
    follow_up_question = response.choices[0].message.content.strip()
    
    # Store the follow-up question
    question_data = {
        'conversation_id': conversation_id,
        'question_number': question_number + 1,
        'question_text': follow_up_question,
        'question_type': 'follow_up',
        'chunks_used': []  # Follow-ups don't use chunks directly
    }
    supabase.table('conversation_questions').insert(question_data).execute()
    
    # Update conversation turn
    supabase.table('conversations').update({
        'current_turn': current_turn + 1
    }).eq('id', conversation_id).execute()
    
    # After 5 turns, generate synthesis
    if current_turn + 1 >= 5:
        return generate_synthesis(conversation_id)
    
    return jsonify({
        "follow_up_question": follow_up_question,
        "current_turn": current_turn + 1,
        "remaining_turns": max(0, 5 - (current_turn + 1))
    })
@app.route("/api/generate-synthesis", methods=["POST"])

def generate_synthesis():
    """After 5 turns, synthesize the conversation into insights"""
    conversation_id = request.json.get("conversation_id")
    
    # Get all Q&A
    questions = supabase.table('conversation_questions').select('*').eq('conversation_id', conversation_id).order('question_number').execute()
    answers = supabase.table('conversation_answers').select('*').eq('conversation_id', conversation_id).execute()
    
    # Get conversation and deck info
    conv_result = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
    deck_id = conv_result.data[0]['deck_id']
    deck_result = supabase.table('uploaded_decks').select('*').eq('id', deck_id).execute()
    
    # Build full conversation
    full_conversation = []
    for q in questions.data:
        full_conversation.append(f"Q{q['question_number']}: {q['question_text']}")
        for a in answers.data:
            if a['question_number'] == q['question_number']:
                full_conversation.append(f"A{q['question_number']}: {a['answer_text']}")
    
    # Generate synthesis
    prompt = f"""
    Analyze this documentary development conversation and provide a synthesis.
    
    PROJECT: {deck_result.data[0]['original_filename']}
    
    FULL CONVERSATION:
    {chr(10).join(full_conversation)}
    
    Create a synthesis that includes:
    
    1. KEY INSIGHTS: What emerged from the conversation
    2. NARRATIVE STRENGTHS: What's working in their story
    3. NARRATIVE GAPS: What's still missing or unclear
    4. CORE THEME: The deeper story they're really telling
    5. NEXT STEPS: Specific recommendations for development
    
    Be specific, reference their actual story details, and provide actionable feedback.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are synthesizing a documentary development conversation. Be insightful and specific."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=1500
    )
    
    synthesis_text = response.choices[0].message.content

    # ============ STORY METRICS CALCULATION ============
    try:
        from src.api.story_metrics import StoryMetricsAnalyzer
        metrics_analyzer = StoryMetricsAnalyzer()
        
        # Get deck text for metrics
        deck_result = supabase.table('uploaded_decks').select('*').eq('id', deck_id).single().execute()
        deck_text = deck_result.data.get('extracted_text') if deck_result.data and deck_result.data.get('extracted_text') else ''
        
        # Get conversation answers
        answers_result = supabase.table('conversation_answers').select('*').eq('conversation_id', conversation_id).execute()
        
        conversation_data = {
            'answers': answers_result.data if answers_result.data else []
        }
        
        # Calculate metrics
        metrics = metrics_analyzer.generate_metrics_summary(deck_text, conversation_data)
        print(f"✅ Metrics calculated successfully")
        
    except Exception as e:
        print(f"⚠️ Metrics calculation failed: {e}")
        metrics = None


    
    # ============ ACADEMIC FRAMEWORK ENHANCEMENT ============
    ENABLE_ACADEMIC_FRAMEWORKS = True
    print(f"DEBUG: ENABLE_ACADEMIC_FRAMEWORKS = {ENABLE_ACADEMIC_FRAMEWORKS}")
    print(f"DEBUG: questions.data exists = {bool(questions.data)}")
    print(f"DEBUG: answers.data exists = {bool(answers.data)}")
    if ENABLE_ACADEMIC_FRAMEWORKS:
        try:
            print("Applying academic framework analysis...")
            framework_conversation_data = {
                'questions': questions.data if questions.data else [],
                'answers': answers.data if answers.data else []
            }
            from academic_frameworks import AcademicFrameworkAnalyzer
            analyzer = AcademicFrameworkAnalyzer()
            enhanced_synthesis_text = analyzer.enhance_synthesis(
                synthesis_text,
                framework_conversation_data,
                ['cognitive_load', 'liminality', 'social_identity', 'documentary_mode']
            )
            synthesis_text = enhanced_synthesis_text
            print("Academic frameworks applied successfully")
        except Exception as e:
            print(f"Framework enhancement failed: {e}")
    # ============ END OF ENHANCEMENT ============

    
    # Store synthesis
    synthesis_data = {
        'conversation_id': conversation_id,
        'full_synthesis': synthesis_text,
        'conversation_data': {
            'total_questions': len(questions.data),
            'total_answers': len(answers.data)
        }
    }
    supabase.table('conversation_synthesis').insert(synthesis_data).execute()
    
    # Mark conversation as complete
    supabase.table('conversations').update({
        'status': 'complete'
    }).eq('id', conversation_id).execute()
    
    return jsonify({
        "synthesis": synthesis_text,
        "metrics": metrics if 'metrics' in locals() else None,
        "conversation_complete": True,
        "total_exchanges": len(answers.data)
    })

@app.route('/templates/<path:filename>')
def serve_template(filename):
    return send_from_directory("src/api/templates", filename)

@app.route('/')
def root_page():
    return render_template('index.html')

@app.route('/test')
def test():
    return 'TEST WORKS'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

