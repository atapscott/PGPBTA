from storyworld.entities import Entity, PlayerCharacter
from utils import utils


class Player:

    character: PlayerCharacter = None
    name: str = None
    id: str = None

    def __init__(self, **kwargs):

        self.__dict__ = kwargs
        self.id = utils.get_id()


class MasterOfCeremonies:

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
