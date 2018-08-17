from storyworld.nl_renderer import NLRenderer
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


def pprint_list(input_list: list, mode='neutral'):
    filtered_input_list: list = []

    if mode == 'article':
        for i in input_list:
            filtered_input_list.append("{} {}".format(NLRenderer.gender_flex('_sda', i[1]), i[0]))

    else:
        filtered_input_list = input_list

    s: str = ''
    for i, element in enumerate(filtered_input_list):
        if i == 0:
            s += element
        elif i == len(filtered_input_list)-1:
            s += ' y ' + element
        else:
            s += ', ' + element

    return s
