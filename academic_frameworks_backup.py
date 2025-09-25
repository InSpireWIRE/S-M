# academic_frameworks.py
"""
Academic Framework Analysis Layer for S!M Synthesis Enhancement
Applies cognitive, anthropological, and psychological lenses to documentary synthesis
"""

import logging
from typing import Dict, List, Optional
import openai

class AcademicFrameworkAnalyzer:
    """Applies academic framework lenses to synthesis output"""
    
    def __init__(self):
        pass  # Using global openai
        self.frameworks = {
            'cognitive_load': self._analyze_cognitive_load,
            'liminality': self._analyze_liminality, 
            'social_identity': self._analyze_social_identity
        }
        
    def enhance_synthesis(self, 
                         baseline_synthesis: str, 
                         conversation_data: Dict,
                         frameworks_to_apply: List[str] = None) -> str:
        """
        Enhances baseline synthesis with academic framework analysis
        
        Args:
            baseline_synthesis: The existing synthesis text
            conversation_data: Full conversation Q&A pairs
            frameworks_to_apply: Which frameworks to use (default: all)
        
        Returns:
            Enhanced synthesis with framework-based insights
        """
        if not frameworks_to_apply:
            frameworks_to_apply = list(self.frameworks.keys())
            
        enhancements = []
        
        for framework in frameworks_to_apply:
            try:
                enhancement = self.frameworks[framework](
                    baseline_synthesis, 
                    conversation_data
                )
                if enhancement:
                    enhancements.append(enhancement)
            except Exception as e:
                logging.error(f"Framework {framework} failed: {e}")
                continue
                
        if not enhancements:
            return baseline_synthesis
            
        # Combine baseline with enhancements
        enhanced_output = f"{baseline_synthesis}\n\n"
        enhanced_output += "## **Framework-Based Story Options**\n\n"
        enhanced_output += "*These insights come from applying academic lenses to your project. "
        enhanced_output += "Think of them as creative options to explore, not prescriptions.*\n\n"
        enhanced_output += "\n\n".join(enhancements)
        
        return enhanced_output
    
    def _analyze_cognitive_load(self, synthesis: str, data: Dict) -> Optional[str]:
        """Apply Cognitive Load Theory analysis"""
        
        prompt = f"""
        Based on this documentary conversation and synthesis, apply Cognitive Load Theory 
        to identify information complexity issues and pacing opportunities.
        
        SYNTHESIS: {synthesis}
        
        CONVERSATION DATA: {self._format_conversation(data)}
        
        Provide 2-3 specific, conversational suggestions about:
        - Where information density might overwhelm audiences
        - Strategic sequencing of revelations
        - Pacing breaks for processing complex elements
        
        Frame all suggestions as creative options using phrases like:
        - "You might consider..."
        - "One approach could be..."
        - "It might be worth exploring..."
        
        Keep tone like a producer giving notes in a development meeting.
        Start with: [Framework: Cognitive Load Theory - Psychology]
        
        Limit response to 150 words.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are a story consultant applying psychological frameworks to help filmmakers. Be conversational and practical."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Cognitive load analysis failed: {e}")
            return None
    
    def _analyze_liminality(self, synthesis: str, data: Dict) -> Optional[str]:
        """Apply Liminality Theory analysis"""
        
        prompt = f"""
        Apply Liminality Theory (anthropology) to identify threshold moments and 
        transitional states with dramatic potential in this documentary.
        
        SYNTHESIS: {synthesis}
        
        CONVERSATION DATA: {self._format_conversation(data)}
        
        Identify 2-3 specific liminal spaces where subjects are between states:
        - Characters between old and new identities
        - Communities in transition
        - Moments of suspended reality
        - The "no longer but not yet" periods
        
        Frame insights conversationally like a producer's notes:
        - "There's rich territory in the period between..."
        - "This liminal moment where [character] is no longer X but not yet Y..."
        - "The threshold state could reveal..."
        
        Start with: [Framework: Liminality Theory - Anthropology]
        
        Limit response to 150 words.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are a story consultant finding dramatic potential in transitional moments. Be specific and conversational."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Liminality analysis failed: {e}")
            return None
    
    def _analyze_social_identity(self, synthesis: str, data: Dict) -> Optional[str]:
        """Apply Social Identity Theory analysis"""
        
        prompt = f"""
        Apply Social Identity Theory to map group loyalties and identity conflicts
        that create natural dramatic tension in this documentary.
        
        SYNTHESIS: {synthesis}
        
        CONVERSATION DATA: {self._format_conversation(data)}
        
        Identify 2-3 identity tensions where characters face competing group memberships:
        - Family vs community loyalties
        - Professional vs personal identities
        - Old allegiances vs new realities
        - In-group vs out-group dynamics
        
        Frame as creative opportunities in producer-note style:
        - "The tension between their role as X and Y could..."
        - "When they must choose between [group A] and [group B]..."
        - "Their shifting group identity might reveal..."
        
        Start with: [Framework: Social Identity Theory - Social Psychology]
        
        Limit response to 150 words.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are identifying character tensions through group identity conflicts. Be specific and actionable."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Social identity analysis failed: {e}")
            return None
    
    def _format_conversation(self, data: Dict) -> str:
        """Format conversation data for prompt inclusion"""
        formatted = []
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        
        for q, a in zip(questions, answers):
            formatted.append(f"Q: {q.get('question_text', '')}")
            formatted.append(f"A: {a.get('answer_text', '')}\n")
            
        # Limit to first 1000 characters to avoid token limits
        conversation_text = "\n".join(formatted)
        if len(conversation_text) > 1000:
            conversation_text = conversation_text[:1000] + "..."
            
        return conversation_text
