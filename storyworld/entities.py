from utils import utils
from storyworld.nl_renderer import NLRenderer


class Entity:

    def __init__(self, **kwargs):

        self.name: str = None
        self.id: str = None
        self.attributes: dict = None

        self.__dict__ = kwargs

        if 'id' not in self.__dict__:
            self.id = utils.get_id()

        if 'gender' not in self.__dict__:
            self.gender = 'f'

    def is_player_character(self) -> bool:
        return isinstance(self, PlayerCharacter)

    def has_playbook_type(self, playbook_name: str):
        return isinstance(self, PlayerCharacter) and self.attributes['playbook_name'] == playbook_name

    def has_attribute(self, attribute_key: str) -> bool:
        return attribute_key in self.attributes.keys()

    def get_attribute(self, attribute_key: str):
        return self.attributes[attribute_key]

    def add_attribute(self, attribute_key: str, increment: int):
        try:
            assert attribute_key in self.attributes.keys()
        except AssertionError:
            self.attributes[attribute_key] = 0

        self.attributes[attribute_key] += increment

    def set_attribute(self, attribute_key: str, value):
        try:
            assert attribute_key in self.attributes.keys()
        except AssertionError:
            self.attributes[attribute_key] = 0

        self.attributes[attribute_key] = value

    def print_nice_name(self):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Agent(Entity):

    def __init__(self, **kwargs):
        self.moves: list = []
        super(Agent, self).__init__(**kwargs)


class PlayerCharacter(Agent):

    def __init__(self, **kwargs):
        super(PlayerCharacter, self).__init__(**kwargs)

    def print_nice_name(self):
        return NLRenderer.get_rendered_nl('long_name',
                                          render_data={'entity_type': 'pc', 'name': self.name, 'gender': self.gender,
                                                    'playbook_name': self.attributes['playbook_name']})


class Threat(Agent):

    def __init__(self, **kwargs):
        super(Threat, self).__init__(**kwargs)

    def print_nice_name(self):
        return NLRenderer.get_rendered_nl('long_name',
                                          render_data={'entity_type': 'threat', 'name': self.name,
                                                       'gender': self.gender,
                                                       'impulse': self.attributes['impulse'],
                                                       'threat_type_name': self.attributes['threat_type_name']})
