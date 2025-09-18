import os
from openai import OpenAI
from typing import Dict, List
import json

class EnhancedSynthesizer:
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.enabled = True
        else:
            self.enabled = False
    
    def analyze_conversation(self, turns: List[Dict], original_analysis: Dict) -> Dict:
        """Generate AI-powered insights from conversation"""
        
        if not self.enabled:
            return {"error": "OpenAI API not configured"}
        
        transcript = self._build_transcript(turns)
        
        # Don't run if no conversation data
        if not transcript.strip():
            return {"error": "No conversation data to analyze"}
        
        prompt = f"""
        Analyze this documentary pitch conversation.
        
        Gaps: {json.dumps(original_analysis.get('style_gaps', []), indent=2)}
        
        Conversation:
        {transcript}
        
        Provide specific analysis:
        1. NARRATIVE ARC - Story evolution
        2. CHARACTER DEPTH - Protagonist compelling factors
        3. VISUAL OPPORTUNITIES - Impactful scenes
        4. PRODUCTION INSIGHTS - Feasibility assessment
        5. UNIQUE ANGLE - Differentiation
        
        Return JSON with keys: narrative_arc, character_analysis, visual_opportunities, production_notes, unique_angle
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a documentary story consultant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {"raw_analysis": content}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _build_transcript(self, turns: List[Dict]) -> str:
        transcript = []
        for turn in turns:
            if turn.get('user_response'):
                transcript.append(f"Q: {turn['system_prompt']}")
                transcript.append(f"A: {turn['user_response']}")
        return "\n".join(transcript)
    
    def estimate_cost(self, turns: List[Dict]) -> float:
        tokens = len(str(turns)) / 4 + 1000
        return round(tokens * 0.002 / 1000, 4)