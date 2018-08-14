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


def pprint_list(input_list: list):
    s: str = ''
    for i, element in enumerate(input_list):
        if i == 0:
            s += element
        elif i == len(input_list)-1:
            s += ' y ' + element
        else:
            s += ', ' + element
    return s
