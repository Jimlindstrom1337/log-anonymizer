from faker import Faker
import random

fake = Faker("sv_SE")


def replace(entity_type, original, lexicon):
    if lexicon.has(original):
        return lexicon.get(original)["replacement"]

    value = _generate(entity_type)
    lexicon.set(original, value, entity_type)
    return value


def _generate(entity_type):
    if entity_type == "personnummer":
        return _fake_personnummer()
    if entity_type == "email":
        return fake.email()
    if entity_type == "phone":
        return fake.phone_number()
    if entity_type == "ip_address":
        return _fake_ip()
    if entity_type == "ipv6":
        return fake.ipv6()
    return "REDACTED"


def _fake_personnummer():
    year = random.randint(1950, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    suffix = random.randint(1000, 9999)
    return f"{year % 100:02d}{month:02d}{day:02d}-{suffix}"


def _fake_ip():
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
