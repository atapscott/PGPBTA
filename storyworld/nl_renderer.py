from jinja2 import Environment, BaseLoader
import json
import random
from utils import utils
import importlib

class NLRenderer:

    _template_data: dict = None
    _localization_data: dict = None
    _gender_flex_data: dict = None
    _env: Environment = None
    storyworld = None

    @classmethod
    def gender_flex(cls, base, gender):

        base = base.lower()

        if gender == 'm':
            index = 0
        elif gender == 'f':
            index = 1
        elif gender == 'mp':
            index = 2
        elif gender == 'fp':
            index = 3
        else:
            raise ValueError('Unkown gender {}'.format(gender))

        if base in cls._gender_flex_data.keys():
            return cls._gender_flex_data[base][index]

        elif base[-1] == 'o':
            if gender == 'f':
                return base[:-1] + 'a'
            elif gender == 'mp':
                return base[:-1] + 'os'
            elif gender == 'fp':
                return base[:-1] + 'as'
            else:
                return base



        elif base[-2:] == 'ón':
            if gender == 'f':
                return base[:-2] + 'ona'

            elif gender == 'mp':
                return base[:-2] + 'ones'

            elif gender == 'fp':
                return base[:-2] + 'onas'

            else:
                return base


        elif base[-2:] == 'en':
            if 'p' in gender:
                return base[:-2] + 'enes'
            else:
                return base

        elif base[-1] in ('e', 'a'):
            if 'p' in gender:
                return base + 's'
            else:
                return base

        elif base[-2:] in ('il', 'al'):
            if 'p' in gender:
                return base + 'es'
            else:
                return base

        elif base[-2:] == 'ún':
            if 'p' in gender:
                return base[-2:] + 'unes'
            else:
                return base

        elif base[-2:] == 'or':
            if gender == 'f':
                return base[:-2] + 'ora'

            elif gender == 'mp':
                return base[:-2] + 'ones'

            elif gender == 'fp':
                return base[:-2] + 'oras'

            else:
                return base

        elif base[-1] == 'r':
            return base+'a' if gender == 'f' else base

        else:
            return base

    @classmethod
    def localize(cls, input):
        return cls._localization_data[input.lower()]

    @classmethod
    def generate(cls, generator_key, delete_result_from_seeder: bool = True):
        generated_item = cls.storyworld.get_generator_data_item(generator_key, delete_result_from_seeder)
        return generated_item

    @classmethod
    def generate_list(cls, generator_key, amount: int, delete_result_from_seeder: bool = True):
        return_list: list = []
        while amount > 0:
            return_list.append(cls.storyworld.get_generator_data_item(generator_key, delete_result_from_seeder))
            amount -= 1
        return return_list

    @classmethod
    def utils_filter(cls, input, filter, *args):
        func = getattr(utils, filter)
        return func(input, *args)

    @classmethod
    def initialize(cls, **kwargs):
        cls._load_template_data()
        cls._load_localization_data()
        cls._load_gender_flex_data()
        cls._env = Environment(loader=BaseLoader())
        cls.storyworld = kwargs['storyworld']

        cls._env.filters['localize'] = cls.localize
        cls._env.filters['gender_flex'] = cls.gender_flex
        cls._env.filters['generate'] = cls.generate
        cls._env.filters['generate_list'] = cls.generate_list
        cls._env.filters['utils_filter'] = cls.utils_filter

    @classmethod
    def embellish(cls, sentence) -> str:

        prep_art: dict = {
            " de el ": " del ",
            " a el ": " al "
        }

        for prep_art_k, prep_art_v in prep_art.items():
            if prep_art_k in sentence:
                sentence = sentence.replace(prep_art_k, prep_art_v)

        return sentence

    @classmethod
    def get_rendered_nl(cls, template_id: str, render_data: dict=None)->str:
        if not render_data:
            render_data = dict()

        template_string: str = random.choice(cls._template_data[template_id])

        rendered_template = cls._render_template(template_string, render_data)

        rendered_template = cls.embellish(rendered_template)

        return rendered_template

    @classmethod
    def has_template(cls, template_id: str)->bool:
        return template_id in cls._template_data.keys()

    @classmethod
    def _load_template_data(cls):
        with open('data/templates.json', 'r', encoding='utf8') as infile:
            cls._template_data = json.load(infile)

    @classmethod
    def _load_localization_data(cls):
        with open('data/localizations.json', 'r', encoding='utf8') as infile:
            cls._localization_data = json.load(infile)

    @classmethod
    def _load_gender_flex_data(cls):
        with open('data/gender_flex.json', 'r', encoding='utf8') as infile:
            cls._gender_flex_data = json.load(infile)

    @classmethod
    def _render_template(cls, template_string: str, render_data: dict)->str:
        rendered_template = cls._env.from_string(template_string)
        render_data['import'] = importlib.import_module
        return rendered_template.render(**render_data)

