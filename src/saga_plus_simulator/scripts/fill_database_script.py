import random

from saga_plus_simulator.database import SessionLocal
from saga_plus_simulator.models import Product


def product_factory() -> Product:
    return Product(name=generate_name(random.randint(0, 9)), price=generate_price())


def generate_price() -> int:
    return random.randint(1, 2000)


def generate_name(name_id: int) -> str:
    names = [
            "Mouse",
             "GPU",
             "Monitor",
             "Keyboard",
             "Motherboard",
             "CPU",
             "Soundcard",
             "RAM",
             "SSD",
             "HDD"
             ]
    symbols = [
        "AED-20194398",
        "QWE-84933",
        "RTY-556677",
        "SDFG-99034",
        "WRTYG-288v6f6",
        "DFTY-0048739",
        "ZXCV-68748845",
        "MNBV-23982",
        "QUWYII-99982",
        "WEHDU-48938939",
        "WOIUE-398475",
        "IUH-30948",
        '03984-340983',
        "93820-293847",
        "093482-23948",
        "2309-2093",
        "WOIU-234-UH",
        "OIU-23234_098",
        "OIWWUE-2344-0384",
        "iauwe-234o8-iuyer",
    ]
    return names[name_id]+ " " + random.choice(symbols)


with SessionLocal() as db:
    for _ in range(0, 100):
        db.add(product_factory())
    db.commit()

