FIELDS = {
    "what_happened",
    "why_it_matters",
    "adviser_relevance",
    "client_impact",
    "market_significance",
}

def word_count(text):
    return len(text.split())

def validate_interpretation(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        return False

    if not all(
        isinstance(data[key], str) and data[key].strip()
        for key in FIELDS
    ):
        return False

    if not 25 <= word_count(data["what_happened"]) <= 40:
        return False

    if not 20 <= word_count(data["why_it_matters"]) <= 30:
        return False

    return True
