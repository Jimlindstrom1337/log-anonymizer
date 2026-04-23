import re

PHONE_LETTERS = [chr(65 + i) for i in range(26)]  # A, B, C...


def assign_placeholders(matches):
    """Return a dict mapping original → placeholder for all unique originals."""
    mapping = {}
    type_indices = {}
    for _, _, entity_type, original in matches:
        if original in mapping:
            continue
        idx = type_indices.get(entity_type, 0) + 1
        type_indices[entity_type] = idx
        mapping[original] = _make_placeholder(entity_type, original, idx, None)

    return mapping


def _personnummer_correct(original):
    return len(re.sub(r'\D', '', original)) == 12


def _make_placeholder(entity_type, original, idx, total):
    if entity_type == "phone":
        label = PHONE_LETTERS[idx - 1] if idx - 1 < len(PHONE_LETTERS) else str(idx)
        return f"[{label}-part]"

    if entity_type == "personnummer":
        status = "Korrekt" if _personnummer_correct(original) else "Fel"
        return f"[Personnummer - {status} {idx}]"

    if entity_type == "email":
        return f"[E-post {idx}]"

    if entity_type in ("ip_address", "ipv6"):
        return f"[IP-adress {idx}]"

    return f"[{entity_type} {idx}]"
