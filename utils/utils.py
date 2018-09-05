from storyworld.nl_renderer import NLRenderer
import uuid
import random


def get_id()->str:
    return str(uuid.uuid4())


def parse_complex_value(complex_value: dict, **kwargs):
    type: str = complex_value['type']

    if type == 'RAND':
        return random.choice(complex_value['values'])
    elif type == 'EVAL':
        if 'imports' in complex_value.keys():
            for imp in complex_value['imports']:
                exec(imp)
        return eval(complex_value['value'])
    else:
        raise ValueError('Unknown complex value type {}'.format(type))


def pprint_list(input_list: list, mode='neutral', *args):
    filtered_input_list: list = []

    if mode == 'article':
        for i in input_list:
            filtered_input_list.append("{} {}".format(NLRenderer.gender_flex('_sda', i[1]), i[0]))

    elif mode == 'gender':
        for i in input_list:
            filtered_input_list.append(NLRenderer.gender_flex(i, args[0]))

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


def weighted_choice(indexed_choices: dict):
    if list(indexed_choices.values()).count(list(indexed_choices.values())[0]) == len(indexed_choices.values()):
        return random.choice(list(indexed_choices.keys()))

    choices = list(indexed_choices.keys())
    weights = list(indexed_choices.values())
    weights = [1-(float(i)/max(weights)) if max(weights) > 0 else i for i in weights]

    return random.choices(choices, weights)[0]
