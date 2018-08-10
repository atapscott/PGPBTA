from jinja2 import Environment, BaseLoader
import json
import random


class NLRenderer:

    _template_data: dict = None
    _localization_data: dict = None
    _gender_flex_data: dict = None
    _env: Environment = None
    storyworld = None

    @classmethod
    def gender_flex(cls, base, gender):
        index = 0 if gender == 'm' else 1
        if base in cls._gender_flex_data.keys():
            return cls._gender_flex_data[base][index]

        elif base[-1] == 'o':
            return base[:-1]+'a' if gender == 'f' else base

        elif base[-2:] == 'ón':
            return base[:-2]+'ona' if gender == 'f' else base

        elif base[-1] == 'r':
            return base+'a' if gender == 'f' else base

        else:
            return base

    @classmethod
    def localize(cls, input):
        return cls._localization_data[input.lower()]

    @classmethod
    def generate(cls, generator_key):
        generated_item = cls.storyworld.get_generator_data_item(generator_key)
        return generated_item

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

    @classmethod
    def get_rendered_nl(cls, template_id: str, render_data: dict=None)->str:
        if not render_data:
            render_data = dict()

        template_string: str = random.choice(cls._template_data[template_id])

        rendered_template = cls._render_template(template_string, render_data)

        return rendered_template

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

        return rendered_template.render(**render_data)

