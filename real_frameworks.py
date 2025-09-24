"""
Real academic frameworks for documentary analysis
Based on actual published research, not keyword counting
"""

# Propp's 31 Narrative Functions (adapted for documentary)
# From "Morphology of the Folktale" (1928)
PROPP_FUNCTIONS = {
    'absentation': {
        'markers': ['leaves', 'departs', 'dies', 'disappears', 'goes away', 'abandons'],
        'description': 'Someone leaves or is removed from the situation'
    },
    'interdiction': {
        'markers': ['warned', 'forbidden', 'told not to', 'cautioned', 'advised against'],
        'description': 'A warning or rule is given'
    },
    'violation': {
        'markers': ['breaks', 'violates', 'ignores', 'defies', 'disobeys'],
        'description': 'The warning/rule is violated'
    },
    'reconnaissance': {
        'markers': ['investigates', 'searches', 'seeks', 'questions', 'explores'],
        'description': 'Villain seeks information'
    },
    'delivery': {
        'markers': ['reveals', 'discovers', 'learns', 'finds out', 'uncovers'],
        'description': 'Information is obtained'
    },
    'trickery': {
        'markers': ['deceives', 'tricks', 'disguises', 'pretends', 'lies'],
        'description': 'Villain attempts deception'
    },
    'complicity': {
        'markers': ['believes', 'trusts', 'falls for', 'deceived by'],
        'description': 'Victim is deceived'
    },
    'villainy': {
        'markers': ['harms', 'kills', 'steals', 'destroys', 'ruins'],
        'description': 'Villain causes harm'
    },
    'lack': {
        'markers': ['needs', 'lacks', 'wants', 'desires', 'missing'],
        'description': 'Something important is missing'
    },
    'mediation': {
        'markers': ['calls for help', 'announces', 'summons', 'requests'],
        'description': 'Misfortune is made known'
    },
    'departure': {
        'markers': ['sets out', 'begins journey', 'leaves home', 'starts quest'],
        'description': 'Hero leaves on mission'
    },
    'struggle': {
        'markers': ['fights', 'battles', 'confronts', 'challenges', 'opposes'],
        'description': 'Direct combat/confrontation'
    },
    'victory': {
        'markers': ['defeats', 'wins', 'overcomes', 'succeeds', 'triumphs'],
        'description': 'Villain is defeated'
    },
    'return': {
        'markers': ['returns', 'comes back', 'arrives home', 'reaches'],
        'description': 'Hero returns'
    },
    'recognition': {
        'markers': ['recognized', 'revealed', 'identified', 'discovered to be'],
        'description': 'Hero is recognized'
    }
}

# Syd Field's Three-Act Structure (adapted for documentary)
# From "Screenplay: The Foundations of Screenwriting" (1979)
THREE_ACT_STRUCTURE = {
    'act_1_setup': {
        'position': (0.0, 0.25),
        'beats': {
            'opening_image': (0.0, 0.05),
            'theme_stated': (0.05, 0.10),
            'setup': (0.0, 0.10),
            'catalyst': (0.10, 0.12),
            'debate': (0.12, 0.25)
        },
        'required_elements': ['protagonist', 'world', 'problem', 'stakes']
    },
    'act_2_confrontation': {
        'position': (0.25, 0.75),
        'beats': {
            'break_into_2': (0.25, 0.27),
            'b_story': (0.27, 0.30),
            'fun_and_games': (0.30, 0.50),
            'midpoint': (0.48, 0.52),
            'bad_guys_close_in': (0.52, 0.65),
            'all_is_lost': (0.65, 0.70),
            'dark_night': (0.70, 0.75)
        },
        'required_elements': ['escalation', 'obstacles', 'transformation', 'crisis']
    },
    'act_3_resolution': {
        'position': (0.75, 1.0),
        'beats': {
            'break_into_3': (0.75, 0.80),
            'finale': (0.80, 0.95),
            'final_image': (0.95, 1.0)
        },
        'required_elements': ['climax', 'resolution', 'new_equilibrium']
    }
}

# Bill Nichols' Documentary Modes
# From "Introduction to Documentary" (2001)
DOCUMENTARY_MODES = {
    'expository': {
        'markers': ['voice-over', 'authority', 'explains', 'informs', 'argues'],
        'characteristics': 'Direct address to viewer, argumentative logic'
    },
    'observational': {
        'markers': ['observes', 'watches', 'no intervention', 'fly on wall'],
        'characteristics': 'No filmmaker intervention, pure observation'
    },
    'participatory': {
        'markers': ['interviews', 'interacts', 'participates', 'engages'],
        'characteristics': 'Filmmaker actively engages with subjects'
    },
    'reflexive': {
        'markers': ['questions', 'self-aware', 'process', 'making of'],
        'characteristics': 'Draws attention to construction of documentary'
    },
    'performative': {
        'markers': ['personal', 'subjective', 'emotional', 'experience'],
        'characteristics': 'Emphasizes subjective experience'
    },
    'poetic': {
        'markers': ['abstract', 'artistic', 'mood', 'atmosphere', 'visual'],
        'characteristics': 'Emphasizes visual associations, tonal qualities'
    }
}

# Plutchik's Wheel of Emotions (for emotional archaeology)
# From psychological research on emotion classification
EMOTION_CATEGORIES = {
    'joy': {
        'basic': ['joy', 'happy', 'pleased'],
        'intense': ['ecstatic', 'elated', 'overjoyed'],
        'mild': ['content', 'satisfied', 'cheerful']
    },
    'trust': {
        'basic': ['trust', 'accept', 'believe'],
        'intense': ['admire', 'devoted', 'worship'],
        'mild': ['tolerate', 'patient', 'calm']
    },
    'fear': {
        'basic': ['fear', 'scared', 'afraid'],
        'intense': ['terror', 'panic', 'hysteria'],
        'mild': ['worried', 'anxious', 'nervous']
    },
    'surprise': {
        'basic': ['surprise', 'shocked', 'amazed'],
        'intense': ['astonished', 'astounded', 'stunned'],
        'mild': ['confused', 'startled', 'wondering']
    },
    'sadness': {
        'basic': ['sad', 'unhappy', 'sorrowful'],
        'intense': ['grief', 'despair', 'depression'],
        'mild': ['lonely', 'gloomy', 'downcast']
    },
    'disgust': {
        'basic': ['disgust', 'revolted', 'repulsed'],
        'intense': ['loathing', 'hatred', 'detestation'],
        'mild': ['dislike', 'aversion', 'disapproval']
    },
    'anger': {
        'basic': ['anger', 'mad', 'frustrated'],
        'intense': ['rage', 'fury', 'wrath'],
        'mild': ['annoyed', 'irritated', 'grumpy']
    },
    'anticipation': {
        'basic': ['anticipation', 'expecting', 'looking forward'],
        'intense': ['vigilant', 'obsessed', 'passionate'],
        'mild': ['interested', 'attentive', 'thoughtful']
    }
}
