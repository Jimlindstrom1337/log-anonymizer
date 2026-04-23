from .detectors import find_matches
from .replacers import replace
from .lexicon import Lexicon


def anonymize(text, lexicon=None):
    if lexicon is None:
        lexicon = Lexicon()

    matches = find_matches(text)
    if not matches:
        return text, lexicon

    result = []
    prev_end = 0

    for start, end, entity_type, original in matches:
        result.append(text[prev_end:start])
        result.append(replace(entity_type, original, lexicon))
        prev_end = end

    result.append(text[prev_end:])
    return "".join(result), lexicon
