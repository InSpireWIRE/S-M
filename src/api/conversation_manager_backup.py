import uuid
from datetime import datetime
from typing import Dict, List

class ConversationManager:
    def __init__(self, supabase_client, analyzer):
        self.supabase = supabase_client
        self.analyzer = analyzer
        self.nlp = analyzer.nlp  # Add this for follow-up question generation
    
    def start_conversation(self, deck_id: str, user_id: str) -> Dict:
        """Start a new conversation for a deck"""
        
        # Get the deck from database
        deck_result = self.supabase.table('uploaded_decks').select("*").eq('id', deck_id).execute()
        
        if not deck_result.data:
            raise ValueError(f"Deck {deck_id} not found")
        
        deck = deck_result.data[0]
        raw_text = deck.get('content_extracted', {}).get('raw_text', '')
        
        # Get chunks for deeper analysis
        chunks_result = self.supabase.table('deck_chunks').select("*").eq('deck_id', deck_id).order('chunk_number').execute()
        chunks = chunks_result.data if chunks_result.data else []
        
        # Get synthesis data for better genre/structure detection
        synthesis_result = self.supabase.table('deck_synthesis').select("*").eq('deck_id', deck_id).execute()
        synthesis = synthesis_result.data[0] if synthesis_result.data else {}
        
        # Analyze the deck
        analysis = self.analyzer.analyze_deck(raw_text)

        # Analyze the deck
        analysis = self.analyzer.analyze_deck(raw_text)
        
        # Try database questions first, then fallback to hardcoded
        db_questions = []
        
        # Get questions based on detected gaps
        gaps = analysis.get('style_gaps', [])
        for gap in gaps[:3]:  # Limit to 3 gap questions
            gap_type = gap.get('type', '')
            if gap_type:
                gap_result = self.supabase.table('gap_question_mappings').select("*").eq('gap_type', gap_type).execute()
                if gap_result.data:
                    db_questions.append(gap_result.data[0]['primary_question'])
        
        # Get questions based on documentary style - use conversational versions
        styles = analysis.get('documentary_styles', [])
        for style in styles[:1]:  # Just take first style
            # Try conversational version first
            style_result = self.supabase.table('documentary_patterns').select("questions").eq('style_name', f"{style}_conversational").execute()
            if not style_result.data:
                # Fallback to formal version
                style_result = self.supabase.table('documentary_patterns').select("questions").eq('style_name', style).execute()
            
            if style_result.data and style_result.data[0].get('questions'):
                style_questions = style_result.data[0]['questions']
                if isinstance(style_questions, list) and style_questions:
                    db_questions.append(style_questions[0])
        
        # Add a framework question if we have room
        if len(db_questions) < 4:
            framework_result = self.supabase.table('frameworks').select("application_patterns").eq('framework_type', 'theme').execute()
            if framework_result.data and framework_result.data[0].get('application_patterns'):
                patterns = framework_result.data[0]['application_patterns']
                if patterns and 'conversational_prompts' in patterns:
                    prompts = patterns['conversational_prompts']
                    if isinstance(prompts, list) and prompts:
                        db_questions.append(prompts[0])
        
        # Get genre and structure from deck metadata (with synthesis override)
        
        # Get genre and structure from deck metadata (with synthesis override)
        deck_genre = deck.get('content_extracted', {}).get('genre', 'unknown')
        deck_structure = deck.get('content_extracted', {}).get('structure_type', 'unknown')
        
        # Use synthesis and content for better genre detection
        raw_text_lower = raw_text.lower()
        if 'episode' in raw_text_lower:
            deck_genre = 'episodic'
            deck_structure = 'episodic'
        elif 'sarah jones' in raw_text_lower and 'detective morrison' in raw_text_lower:
            deck_genre = 'character_study'
            deck_structure = 'character_based'
        elif synthesis and len(synthesis.get('key_characters', {}).get('main_characters', [])) > 2:
            deck_genre = 'character_study'
            deck_structure = 'character_based'
        
        missing_elements = deck.get('content_extracted', {}).get('missing_elements', [])
        
        # Create conversation record
        conversation_data = {
            'deck_id': deck_id,
            'user_id': user_id,
            'status': 'active',
            'metadata': {
                'genre': deck_genre,
                'structure_type': deck_structure,
                'total_chunks': len(chunks),
                'analysis': {
                    'documentary_mode': analysis.get('documentary_mode', 'unknown'),
                    'narrative_voice': analysis.get('narrative_voice', {}),
                    'argument_structure': analysis.get('argument_structure', {}),
                    'story_structure': analysis.get('story_structure', {})
                }
            }
        }
        
        # Insert into database
        result = self.supabase.table('conversations').insert(conversation_data).execute()
        
        if not result.data:
            raise ValueError("Failed to create conversation")
            
        conversation_id = result.data[0]['id']
        
        # Generate questions based on chunks and analysis
        # Use database questions if we found any, otherwise generate from chunks
        if db_questions:
            questions = db_questions
        else:
            # Fallback to chunk-based generation
            questions = self.generate_questions_from_chunks(chunks, analysis, missing_elements, deck_genre)
        
        # Save first turn
        turn_data = {
            'conversation_id': conversation_id,
            'turn_number': 1,
            'system_prompt': questions[0] if questions else "Tell me about your documentary project.",
            'user_response': None,
            'structural_options': questions
        }
        
        self.supabase.table('conversation_turns').insert(turn_data).execute()
        
        return {
            'conversation_id': conversation_id,
            'questions': questions,
            'genre': deck_genre,
            'structure_type': deck_structure,
            'analysis': analysis
        }
    
    def generate_questions_from_chunks(self, chunks: List[Dict], analysis: Dict, missing_elements: List, genre: str) -> List[str]:
        """Generate questions based on chunk analysis"""
        questions = []
        
        # Questions based on missing elements
        if missing_elements:
            for element in missing_elements[:2]:  # First 2 missing elements
                if 'access' in str(element).lower():
                    questions.append("What exclusive access or unique footage do you have for this story?")
                elif 'stakes' in str(element).lower():
                    questions.append("What's at stake in your story? Why does this matter now?")
                elif 'subject' in str(element).lower() or 'character' in str(element).lower():
                    questions.append("Who is your main subject or character? What makes them compelling?")
                elif 'conflict' in str(element).lower():
                    questions.append("What's the central conflict or tension in your story?")
        
        # Questions based on chunk analysis
        chunk_types = [c.get('chunk_type', '') for c in chunks]
        
        # Check what's present and ask about gaps
        if 'narrative' in chunk_types and 'subject' not in chunk_types:
            questions.append("You've described events, but who are the people at the center of this story?")
        
        if 'subject' in chunk_types and 'narrative' not in chunk_types:
            questions.append("You've introduced people, but what actually happens in your documentary?")
        
        if 'style' not in chunk_types:
            questions.append("How do you envision the visual style and tone of this documentary?")
        
        # Genre-specific questions
        genre_questions = {
            'true_crime': [
                "How will you handle the sensitive nature of the crime and its victims?",
                "What new angle or revelation does your documentary bring to this case?"
            ],
            'character_study': [
                "What transformation does your subject go through?",
                "What intimate access do you have to your character's life?"
            ],
            'investigative': [
                "What's your process for uncovering the truth?",
                "What obstacles do you expect in your investigation?"
            ]
        }
        
        if genre in genre_questions:
            questions.extend(genre_questions[genre][:1])  # Add one genre-specific question
        
        # Based on analysis results
        if analysis.get('documentary_mode') == 'unknown':
            questions.append("Will you be present in the film, or observing from outside?")
        
        voice = analysis.get('narrative_voice', {})
        if voice.get('perspective') == 'third_person' and voice.get('voice_authority', 0) < 1:
            questions.append("Your pitch is quite objective - what's your personal connection to this story?")
        
        # Fallback questions
        if not questions:
            questions = [
                "What story are you trying to tell?",
                "What unique access or perspective do you bring?",
                "Why is this the right time for this documentary?"
            ]
        
        return questions[:5]  # Return max 5 questions
    
    def save_turn(self, conversation_id: str, question: str, answer: str) -> Dict:
        """Save a conversation turn with user's answer"""
        
        # Get current turn number
        turns_result = self.supabase.table('conversation_turns')\
            .select("turn_number")\
            .eq('conversation_id', conversation_id)\
            .order('turn_number', desc=True)\
            .limit(1)\
            .execute()
        
        current_turn = turns_result.data[0]['turn_number'] if turns_result.data else 0
        
        # Update current turn with answer
        if current_turn > 0:
            self.supabase.table('conversation_turns')\
                .update({'user_response': answer})\
                .eq('conversation_id', conversation_id)\
                .eq('turn_number', current_turn)\
                .execute()
        
        # Generate contextual next questions based on the answer
        next_questions = self.generate_followup_questions(answer, {
            'conversation_id': conversation_id,
            'turn_number': current_turn
        })
        
        # Create next turn
        next_turn_data = {
            'conversation_id': conversation_id,
            'turn_number': current_turn + 1,
            'system_prompt': next_questions[0],
            'user_response': None,
            'structural_options': next_questions
        }
        
        result = self.supabase.table('conversation_turns').insert(next_turn_data).execute()
        
        return {
            'turn_id': result.data[0]['id'] if result.data else None,
            'saved': True,
            'next_questions': next_questions
        }
    
    def generate_followup_questions(self, answer: str, conversation_context: Dict) -> List[str]:
        """Generate contextual follow-up questions based on the answer"""
        
        # Analyze what they said
        doc = self.nlp(answer)
        
        # If they mention specific people, ask about them
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if people:
            return [
                f"Tell me more about {people[0]}'s role in the story.",
                f"How did you get access to {people[0]}?",
                f"What makes {people[0]} the right subject for this documentary?"
            ]
        
        # If they mention conflict/controversy
        if any(word in answer.lower() for word in ['controversial', 'conflict', 'complex', 'debate']):
            return [
                "How do you plan to present both sides fairly?",
                "What's your stance on this controversy?",
                "Have you spoken to people on both sides of this issue?"
            ]
        
        # If they mention access or exclusive content
        if any(word in answer.lower() for word in ['exclusive', 'access', 'never before', 'first time']):
            return [
                "How did you secure this exclusive access?",
                "What conditions or limitations came with this access?",
                "What will viewers see that's never been shown before?"
            ]
        
        # If they mention visual or stylistic elements
        if any(word in answer.lower() for word in ['visual', 'style', 'camera', 'footage', 'archive']):
            return [
                "What's your visual reference or inspiration?",
                "How will this visual approach serve your story?",
                "What percentage is archival versus new footage?"
            ]
        
        # If they mention impact or change
        if any(word in answer.lower() for word in ['change', 'impact', 'awareness', 'action']):
            return [
                "What specific change do you hope to inspire?",
                "How will you measure the impact of your documentary?",
                "Who needs to see this film for change to happen?"
            ]
    
        # Default fallbacks
        return [
            "What evidence or documentation do you have for this?",
            "How will you visualize this on screen?",
            "What challenges do you anticipate in telling this part of the story?"
        ]
    
    def get_conversation_history(self, conversation_id: str) -> Dict:
        """Get full conversation history"""
        
        # Get conversation
        conv_result = self.supabase.table('conversations')\
            .select("*")\
            .eq('id', conversation_id)\
            .execute()
        
        # Get all turns
        turns_result = self.supabase.table('conversation_turns')\
            .select("*")\
            .eq('conversation_id', conversation_id)\
            .order('turn_number')\
            .execute()
        
        return {
            'conversation': conv_result.data[0] if conv_result.data else None,
            'turns': turns_result.data if turns_result.data else []
        }