import re
import spacy
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import networkx as nx  # For relationship mapping

class AdvancedDocumentaryChunker:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.nlp = spacy.load("en_core_web_sm")
        self.chunk_graph = nx.DiGraph()  # Directed graph for relationships
        
    def process_deck_advanced(self, deck_id: str, raw_text: str, file_type: str) -> Dict:
        """Multi-pass progressive analysis"""
        
        # Pass 1: Structure Detection & Initial Chunking
        structure = self._detect_deep_structure(raw_text)
        raw_chunks = self._create_semantic_chunks(raw_text, structure)
        
        # Pass 2: Entity & Reference Extraction
        chunks_with_entities = self._extract_entities_and_refs(raw_chunks)
        
        # Pass 3: Relationship Mapping
        connected_chunks = self._build_relationship_graph(chunks_with_entities)
        
        # Pass 4: Semantic Coherence Check
        coherent_chunks = self._ensure_semantic_completeness(connected_chunks)
        
        # Pass 5: Hierarchical Organization
        hierarchical = self._build_hierarchy(coherent_chunks)
        
        # Pass 6: Context Windows
        final_chunks = self._add_context_windows(hierarchical)
        
        # Pass 7: Progressive Synthesis
        synthesis = self._synthesize_analysis(final_chunks)
        
        # Store enhanced chunks
        self._store_advanced_chunks(deck_id, final_chunks, synthesis)
        
        return {
            'chunks': final_chunks,
            'synthesis': synthesis,
            'relationships': self._export_graph(),
            'narrative_flow': self._trace_narrative_path(final_chunks)
        }

    def _detect_deep_structure(self, raw_text: str) -> Dict:
        """Detect the deep structure of the document"""
        lines = raw_text.split('\n')
        structure = {
            'type': 'unknown',
            'sections': [],
            'hierarchy_depth': 0,
            'has_episodes': False,
            'has_clear_headers': False
        }
        
        # Check for headers
        headers = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean and line_clean.isupper() and 3 < len(line_clean) < 100:
                headers.append({'line': i, 'text': line_clean, 'level': 1})
            elif re.match(r'^#{1,3}\s+', line_clean):  # Markdown headers
                level = len(re.match(r'^(#{1,3})\s+', line_clean).group(1))
                headers.append({'line': i, 'text': line_clean, 'level': level})
        
        if len(headers) > 2:
            structure['has_clear_headers'] = True
            structure['sections'] = headers
            
        # Check for episodes
        if re.search(r'(?i)(episode\s+\d+|chapter\s+\d+)', raw_text):
            structure['has_episodes'] = True
            structure['type'] = 'episodic'
        elif structure['has_clear_headers']:
            structure['type'] = 'sectioned'
        else:
            structure['type'] = 'narrative_flow'
            
        return structure
    
    def _create_semantic_chunks(self, raw_text: str, structure: Dict) -> List[Dict]:
        """Create chunks based on semantic coherence - platform agnostic"""
        
        # Clean common UI noise patterns from ANY platform
        raw_text = self._clean_universal_ui_noise(raw_text)
        
        # Process with spaCy for semantic analysis
        doc = self.nlp(raw_text)
        
        chunks = []
        current_chunk = []
        current_entities = set()
        current_semantic_signature = []
        
        for sent in doc.sents:
            # Skip noise (very short fragments, likely UI)
            if len(sent.text.split()) < 3:
                continue
                
            # Extract semantic features
            sent_entities = set([ent.text for ent in sent.ents])
            sent_lemmas = [token.lemma_ for token in sent if token.pos_ in ['NOUN', 'VERB', 'PROPN']]
            sent_deps = [token.dep_ for token in sent]
            
            # Determine if this is a boundary
            is_boundary = self._detect_semantic_boundary(
                current_chunk, 
                current_entities,
                current_semantic_signature,
                sent.text,
                sent_entities,
                sent_lemmas,
                sent_deps
            )
            
            if is_boundary and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text.split()) > 10:  # Minimum semantic unit
                    chunks.append({
                        'id': f"chunk_{len(chunks)}",
                        'content': chunk_text,
                        'header': self._extract_semantic_header(chunk_text, current_entities),
                        'type': 'semantic',
                        'position': len(chunks),
                        'entities': list(current_entities)
                    })
                
                # Start new chunk
                current_chunk = [sent.text]
                current_entities = sent_entities
                current_semantic_signature = sent_lemmas
            else:
                # Continue building chunk
                current_chunk.append(sent.text)
                current_entities.update(sent_entities)
                current_semantic_signature.extend(sent_lemmas)
        
        # Handle final chunk
        if current_chunk and len(' '.join(current_chunk).split()) > 10:
            chunks.append({
                'id': f"chunk_{len(chunks)}",
                'content': ' '.join(current_chunk),
                'header': self._extract_semantic_header(' '.join(current_chunk), current_entities),
                'type': 'semantic',
                'position': len(chunks),
                'entities': list(current_entities)
            })
        
        return chunks
    
    def _detect_semantic_boundary(self, current_chunk, current_entities, current_sig, 
                                  new_sent, new_entities, new_lemmas, new_deps):
        """Detect semantic boundaries using NLP features"""
        
        # No boundary if we're just starting
        if not current_chunk:
            return False
        
        # Boundary detection signals
        signals = []
        
        # 1. Entity continuity check
        if current_entities:
            entity_overlap = len(current_entities.intersection(new_entities)) / len(current_entities)
            signals.append(entity_overlap < 0.3)  # Major entity shift
        
        # 2. Structural markers
        structural_markers = [
            new_sent.strip().isupper() and len(new_sent) < 100,  # Section header
            new_sent.strip().endswith(':'),  # List introduction
            any(new_sent.startswith(m) for m in ['Episode', 'Chapter', 'Part', 'Section']),
            bool(re.match(r'^\d+\.?\s+[A-Z]', new_sent)),  # Numbered section
        ]
        signals.append(any(structural_markers))
        
        # 3. Semantic coherence via lemma overlap
        if current_sig:
            lemma_overlap = len(set(current_sig).intersection(set(new_lemmas))) / len(set(current_sig))
            signals.append(lemma_overlap < 0.1 and len(current_chunk) > 5)  # Topic shift
        
        # 4. Dependency pattern shift (narrative vs descriptive)
        if 'nsubj' in new_deps and 'ROOT' in new_deps:
            # New independent clause, potential boundary
            if len(current_chunk) > 10:  # If chunk is substantial
                signals.append(True)
        
        # Require multiple signals for boundary
        return sum(signals) >= 2
    
    def _clean_universal_ui_noise(self, text: str) -> str:
        """Remove UI elements from ANY platform"""
        
        # Common UI patterns across platforms
        ui_patterns = [
            # Navigation elements
            r'(Previous|Next|Go to) (page|slide)',
            r'Page \d+ of \d+',
            r'\d+\s*/\s*\d+',  # Page numbers
            
            # View controls
            r'(Zoom|View|Show|Hide|Enter|Exit).{0,20}(full ?screen|captions|media)',
            r'Click to.{0,20}(edit|view|expand)',
            
            # Platform signatures (without being specific)
            r'Share\s+(this\s+)?(document|presentation|design)',
            r'Created? (with|using|in)',
            r'Open in.{0,20}(app|browser|tab|window)',
            
            # Repetitive noise
            r'([A-Za-z])\1{5,}',  # Repeated characters (AAAAAA)
            r'[\u2060\u200B\u200C\u200D\uFEFF]',  # Zero-width spaces
            
            # Time/duration markers
            r'\d+\.\d+s',
            r'Loading\.{3,}',
        ]
        
        cleaned = text
        for pattern in ui_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def _extract_semantic_header(self, text: str, entities: set) -> str:
        """Extract or generate semantic header for chunk"""
        
        if not text:  # Handle empty text
            return "Section"
        
        doc = self.nlp(text[:200])  # Analyze beginning
        
        # Look for natural headers
        lines = text.split('\n')
        if lines:
            first_line = lines[0].strip()
            if first_line and len(first_line) < 100 and first_line[0].isupper():
                return first_line
        
        # Use key entities
        if entities:
            key_entities = list(entities)[:2]
            return f"{' & '.join(key_entities)}"
        
        # Extract main topic via noun chunks
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        if noun_chunks:
            return noun_chunks[0].title()
        
        # Fallback to first sentence fragment
        return (text[:50] + '...') if len(text) > 50 else text
    
    def _extract_entities_and_refs(self, chunks: List[Dict]) -> List[Dict]:
        """Extract entities and references from chunks"""
        for chunk in chunks:
            doc = self.nlp(chunk['content'])
            
            chunk['entities'] = {
                'people': [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
                'locations': [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]],
                'organizations': [ent.text for ent in doc.ents if ent.label_ == "ORG"],
                'dates': [ent.text for ent in doc.ents if ent.label_ == "DATE"]
            }
            
            # Detect references
            chunk['references'] = {
                'pronouns': [token.text for token in doc if token.pos_ == "PRON"],
                'has_forward_ref': any(word in chunk['content'].lower() for word in ['below', 'following', 'next']),
                'has_backward_ref': any(word in chunk['content'].lower() for word in ['above', 'previous', 'earlier'])
            }
            
        return chunks
    
    def _build_relationship_graph(self, chunks: List[Dict]) -> List[Dict]:
        """Build a graph of chunk relationships"""
        # Clear previous graph
        self.chunk_graph.clear()
        
        # Add nodes
        for chunk in chunks:
            self.chunk_graph.add_node(
                chunk['id'],
                content=chunk['content'][:100],  # Store first 100 chars
                entities=chunk['entities'],
                position=chunk['position']
            )
        
        # Add edges based on relationships
        for i, chunk in enumerate(chunks):
            # Sequential relationship
            if i > 0:
                self.chunk_graph.add_edge(
                    chunks[i-1]['id'],
                    chunk['id'],
                    type='follows'
                )
            
            # Entity-based relationships
            for j, other in enumerate(chunks):
                if i != j:
                    # Check for shared entities
                    shared_people = set(chunk['entities']['people']).intersection(
                        set(other['entities']['people'])
                    )
                    if shared_people:
                        self.chunk_graph.add_edge(
                            chunk['id'],
                            other['id'],
                            type='shares_people',
                            shared=list(shared_people)
                        )
        
        # Add graph metrics to chunks
        centrality = nx.betweenness_centrality(self.chunk_graph)
        for chunk in chunks:
            chunk['graph_metrics'] = {
                'centrality': centrality.get(chunk['id'], 0),
                'in_degree': self.chunk_graph.in_degree(chunk['id']),
                'out_degree': self.chunk_graph.out_degree(chunk['id'])
            }
        
        return chunks
    
    def _ensure_semantic_completeness(self, chunks: List[Dict]) -> List[Dict]:
        """Ensure each chunk is semantically complete"""
        refined_chunks = []
        
        for i, chunk in enumerate(chunks):
            doc = self.nlp(chunk['content'])
            
            # Check for incomplete opening
            first_sent = list(doc.sents)[0] if doc.sents else None
            if first_sent:
                first_tokens = [t for t in first_sent]
                if first_tokens and first_tokens[0].pos_ == "PRON":
                    # Starts with pronoun - needs context
                    chunk['semantic_completeness'] = {
                        'is_complete': False,
                        'issue': 'starts_with_pronoun',
                        'needs_previous_context': True
                    }
                else:
                    chunk['semantic_completeness'] = {
                        'is_complete': True,
                        'issue': None,
                        'needs_previous_context': False
                    }
            
            refined_chunks.append(chunk)
        
        return refined_chunks        


    def _build_hierarchy(self, chunks: List[Dict]) -> List[Dict]:
        """Build hierarchical structure of chunks"""
        for chunk in chunks:
            # Determine hierarchy level based on content and position
            chunk['hierarchy'] = {
                'level': 1,  # Default level
                'parent': None,
                'children': []
            }
            
            # Opening chunks
            if chunk['position'] == 0:
                chunk['hierarchy']['role'] = 'introduction'
            # Closing chunks
            elif chunk['position'] == len(chunks) - 1:
                chunk['hierarchy']['role'] = 'conclusion'
            # Middle chunks
            else:
                chunk['hierarchy']['role'] = 'body'
                
        return chunks


    def _add_context_windows(self, chunks: List[Dict]) -> List[Dict]:
        """Add context from surrounding chunks"""
        for i, chunk in enumerate(chunks):
            # Previous context
            if i > 0:
                prev_doc = self.nlp(chunks[i-1]['content'])
                prev_sents = list(prev_doc.sents)
                chunk['context_before'] = ' '.join([s.text for s in prev_sents[-2:]]) if len(prev_sents) >= 2 else chunks[i-1]['content']
            else:
                chunk['context_before'] = None
            
            # Next context  
            if i < len(chunks) - 1:
                next_doc = self.nlp(chunks[i+1]['content'])
                next_sents = list(next_doc.sents)
                chunk['context_after'] = ' '.join([s.text for s in next_sents[:2]]) if len(next_sents) >= 2 else chunks[i+1]['content']
            else:
                chunk['context_after'] = None
            
            # Narrative position
            chunk['narrative_position'] = {
                'absolute': i,
                'relative': i / len(chunks) if chunks else 0,
                'quartile': self._get_quartile(i, len(chunks))
            }
        
        return chunks
    
    def _get_quartile(self, position: int, total: int) -> str:
        """Determine which quartile of the document this is in"""
        if total == 0:
            return 'unknown'
        ratio = position / total
        if ratio < 0.25:
            return 'opening'
        elif ratio < 0.5:
            return 'development'
        elif ratio < 0.75:
            return 'climax'
        else:
            return 'resolution'

    def _synthesize_analysis(self, chunks: List[Dict]) -> Dict:
        """Synthesize insights from all chunks"""
        synthesis = {
            'total_chunks': len(chunks),
            'structure_type': chunks[0].get('type', 'unknown') if chunks else 'unknown',
            'key_entities': self._extract_key_entities(chunks),
            'narrative_flow': self._analyze_narrative_flow(chunks),
            'central_themes': self._identify_themes(chunks),
            'pivot_chunks': self._identify_pivot_chunks(chunks)
        }
        
        return synthesis
    
    def _extract_key_entities(self, chunks: List[Dict]) -> Dict:
        """Extract most important entities across all chunks"""
        all_people = []
        all_locations = []
        
        for chunk in chunks:
            all_people.extend(chunk['entities']['people'])
            all_locations.extend(chunk['entities']['locations'])
        
        from collections import Counter
        return {
            'main_characters': Counter(all_people).most_common(5),
            'key_locations': Counter(all_locations).most_common(3)
        }
    
    def _analyze_narrative_flow(self, chunks: List[Dict]) -> str:
        """Determine the narrative flow pattern"""
        if not chunks:
            return 'unknown'
        
        # Check for episodic structure
        if any('episode' in c.get('header', '').lower() for c in chunks):
            return 'episodic'
        
        # Check for chronological
        dates = []
        for chunk in chunks:
            dates.extend(chunk['entities'].get('dates', []))
        if len(dates) > 3:
            return 'chronological'
        
        return 'thematic'
    
    def _identify_themes(self, chunks: List[Dict]) -> List[str]:
        """Identify central themes"""
        themes = []
        
        # Simple keyword-based theme detection
        theme_keywords = {
            'justice': ['justice', 'fair', 'right', 'wrong', 'crime'],
            'transformation': ['change', 'transform', 'become', 'journey'],
            'conflict': ['fight', 'struggle', 'against', 'battle', 'conflict'],
            'discovery': ['discover', 'find', 'reveal', 'uncover', 'truth']
        }
        
        all_text = ' '.join([c['content'].lower() for c in chunks])
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _identify_pivot_chunks(self, chunks: List[Dict]) -> List[str]:
        """Identify chunks that are pivotal to the narrative"""
        pivot_chunks = []
        
        for chunk in chunks:
            # High centrality chunks are pivotal
            if chunk['graph_metrics']['centrality'] > 0.2:
                pivot_chunks.append(chunk['id'])
        
        return pivot_chunks

    def _store_advanced_chunks(self, deck_id: str, chunks: List[Dict], synthesis: Dict):
        """Store the enhanced chunks and synthesis"""
        # Clear existing chunks
        self.supabase.table('deck_chunks').delete().eq('deck_id', deck_id).execute()
        
        # Store each chunk
        for chunk in chunks:
            chunk_data = {
                'deck_id': deck_id,
                'chunk_type': chunk.get('type', 'unknown'),
                'chunk_number': chunk['position'] + 1,
                'chunk_label': chunk.get('header', f"Section {chunk['position'] + 1}"),
                'content': chunk['content'],
                'metadata': chunk.get('entities', {}),
                'graph_metrics': chunk.get('graph_metrics', {}),
                'context_before': chunk.get('context_before'),
                'context_after': chunk.get('context_after'),
                'semantic_completeness': chunk.get('semantic_completeness', {}),
                'relationships': chunk.get('references', {}),
                'narrative_position': chunk.get('narrative_position', {})
            }
            
            self.supabase.table('deck_chunks').insert(chunk_data).execute()
        
        # Store synthesis
        synthesis_data = {
            'deck_id': deck_id,
            'narrative_arc': synthesis.get('narrative_flow'),
            'central_conflict': str(synthesis.get('central_themes', [])),
            'key_characters': synthesis.get('key_entities', {}),
            'thematic_threads': synthesis.get('central_themes', []),
            'structural_integrity': {'total_chunks': synthesis.get('total_chunks', 0)},
            'pivot_points': synthesis.get('pivot_chunks', []),
            'relationship_graph': {}  # We'll add graph export later
        }
        
        self.supabase.table('deck_synthesis').insert(synthesis_data).execute()
    
    def _export_graph(self) -> Dict:
        """Export the relationship graph"""
        return {
            'nodes': list(self.chunk_graph.nodes()),
            'edges': list(self.chunk_graph.edges()),
            'total_nodes': self.chunk_graph.number_of_nodes(),
            'total_edges': self.chunk_graph.number_of_edges()
        }
    
    def _trace_narrative_path(self, chunks: List[Dict]) -> List[str]:
        """Trace the main narrative path through chunks"""
        if not chunks:
            return []
        
        # For now, return the sequential path
        return [chunk['id'] for chunk in chunks]


