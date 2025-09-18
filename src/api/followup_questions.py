# Gap-specific follow-up questions
FOLLOWUP_QUESTIONS = {
    'missing_conflict': {
        'level_1': [
            "OK but WHY can't they just overcome that?",
            "What's REALLY in their way - not just the obvious stuff?",
            "So who's actively working against them?"
        ],
        'level_2': [
            "And if they fail to overcome this?",
            "What's the worst thing that could happen?",
            "Who gets hurt if nothing changes?"
        ]
    },
    'no_transformation': {
        'level_1': [
            "But what changes INSIDE your characters?",
            "How are they different people by the end?",
            "What do they learn that we learn with them?"
        ],
        'level_2': [
            "What moment forces them to change?",
            "What old belief do they have to let go?",
            "How do we SEE this change on screen?"
        ]
    },
    'no_stakes': {
        'level_1': [
            "OK but what happens if your story doesn't get told?",
            "Who suffers if this stays hidden?",
            "What's at risk beyond your characters?"
        ],
        'level_2': [
            "Why THIS story and why NOW?",
            "What bigger issue does this represent?",
            "What will audiences DO after watching?"
        ]
    },
    'unclear_access': {
        'level_1': [
            "How did you earn their trust?",
            "What took you months/years to get them to share?",
            "Why did they choose YOU to tell their story?"
        ],
        'level_2': [
            "What are they risking by letting you film?",
            "What promises did you make to them?",
            "What WON'T you show to protect them?"
        ]
    }
}

def get_followup_for_gap(gap_type: str, level: int = 1) -> list:
    """Get conversational follow-ups for a gap type"""
    return FOLLOWUP_QUESTIONS.get(gap_type, {}).get(f'level_{level}', [
        "Tell me more about that.",
        "Can you go deeper on this?",
        "What else should I know?"
    ])
