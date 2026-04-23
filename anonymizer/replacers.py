from faker import Faker
import random

fake = Faker("sv_SE")
_cache = {}


def _cached(key, generator):
    if key not in _cache:
        _cache[key] = generator()
    return _cache[key]


def reset_cache():
    _cache.clear()


def replace(entity_type, original):
    if entity_type == "personnummer":
        return _cached(original, _fake_personnummer)
    if entity_type == "email":
        return _cached(original, lambda: fake.email())
    if entity_type == "phone":
        return _cached(original, lambda: fake.phone_number())
    if entity_type == "ip_address":
        return _cached(original, _fake_ip)
    if entity_type == "ipv6":
        return _cached(original, lambda: fake.ipv6())
    return original


def _fake_personnummer():
    year = random.randint(1950, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    suffix = random.randint(1000, 9999)
    return f"{year % 100:02d}{month:02d}{day:02d}-{suffix}"


def _fake_ip():
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
