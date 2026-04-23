from .detectors import find_matches
from .replacers import replace, reset_cache


def anonymize(text, reset=True):
    if reset:
        reset_cache()

    matches = find_matches(text)
    if not matches:
        return text, []

    result = []
    prev_end = 0
    replacements = []

    for start, end, entity_type, original in matches:
        result.append(text[prev_end:start])
        fake_value = replace(entity_type, original)
        result.append(fake_value)
        replacements.append({
            "type": entity_type,
            "original": original,
            "replacement": fake_value,
            "position": start,
        })
        prev_end = end

    result.append(text[prev_end:])
    return "".join(result), replacements
