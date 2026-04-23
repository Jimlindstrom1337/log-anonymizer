from .detectors import find_matches
from .replacers import assign_placeholders
from .lexicon import Lexicon


def anonymize(text, lexicon=None):
    if lexicon is None:
        lexicon = Lexicon()

    matches = find_matches(text)
    if not matches:
        return text, lexicon

    mapping = assign_placeholders(matches)

    result = []
    prev_end = 0

    for start, end, entity_type, original in matches:
        result.append(text[prev_end:start])
        placeholder = mapping[original]
        if not lexicon.has(original):
            lexicon.set(original, placeholder, entity_type)
        result.append(placeholder)
        prev_end = end

    result.append(text[prev_end:])
    return "".join(result), lexicon


def deanonymize(text, lexicon):
    """Replace placeholders in text back to original values."""
    reverse_map = {e["replacement"]: e["original"] for e in lexicon.entries()}
    for placeholder, original in sorted(reverse_map.items(), key=lambda x: -len(x[0])):
        text = text.replace(placeholder, original)
    return text
