from utils import utils


class Entity:

    name: str = None
    id: str = None
    attributes: dict = None

    def __init__(self, **kwargs):

        self.__dict__ = kwargs

        if 'id' not in self.__dict__:
            self.id = utils.get_id()

    def is_player_character(self) -> bool:
        return isinstance(self, PlayerCharacter)

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
        return self.print_nice_name()

    def __repr__(self):
        return self.print_nice_name()


class PlayerCharacter(Entity):

    def __init__(self, **kwargs):
        super(PlayerCharacter, self).__init__(**kwargs)

    def print_nice_name(self):
        return '{} the {}'.format(self.name, self.attributes['playbook_name'])


class Threat(Entity):

    def __init__(self, **kwargs):
        super(Threat, self).__init__(**kwargs)

    def print_nice_name(self):
        return '{} the {}'.format(self.name, self.attributes['threat_type'])
