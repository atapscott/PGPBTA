import uuid
import random


def get_id()->str:
    return str(uuid.uuid4())


def parse_complex_value(complex_value: dict):
    type: str = complex_value['type']

    if type == 'RAND':
        return random.choice(complex_value['values'])
    else:
        raise ValueError('Unknown complex value type {}'.format(type))
