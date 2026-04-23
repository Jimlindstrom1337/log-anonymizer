import json


class Lexicon:
    def __init__(self):
        self._map = {}

    def set(self, original, replacement, entity_type):
        self._map[original] = {"replacement": replacement, "type": entity_type}

    def get(self, original):
        return self._map.get(original)

    def has(self, original):
        return original in self._map

    def clear(self):
        self._map.clear()

    def to_dict(self):
        return dict(self._map)

    def entries(self):
        return [
            {"original": original, "replacement": v["replacement"], "type": v["type"]}
            for original, v in self._map.items()
        ]

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._map, f, ensure_ascii=False, indent=2)

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self._map = json.load(f)
