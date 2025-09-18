# Add this to the __init__ method of AdvancedStoryAnalyzer:
from analysis.documentary_style_analyzer import DocumentaryStyleAnalyzer

def __init__(self, supabase_client):
    self.supabase = supabase_client
    try:
        self.nlp = spacy.load("en_core_web_lg")
    except:
        self.nlp = spacy.load("en_core_web_sm")
    self.documentary_analyzer = DocumentaryStyleAnalyzer()  # ADD THIS LINE
    self.frameworks = self._load_frameworks()

# Update the analyze_deck method:
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
    
    return {
        'documentary_styles': documentary_analysis['dominant_styles'],  # NEW
        'style_gaps': documentary_analysis['gaps'],  # NEW
        'documentary_mode': documentary_analysis['dominant_styles'][0] if documentary_analysis['dominant_styles'] else mode,
        'narrative_voice': voice,
        'argument_structure': argument,
        'story_structure': structure,
        'people': people,
        'locations': locations,
        'raw_text_lower': raw_text.lower()
    }
